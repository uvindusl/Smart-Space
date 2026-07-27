import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Gio, Pango, GLib
from service import load_all_apps, launch_app
from rapidfuzz import fuzz

def fuzzy_score(query, text):
    if not query:
        return 100
    if fuzz:
        return fuzz.partial_ratio(query.lower(), text.lower())
    q = query.lower()
    t = text.lower()
    if q in t:
        return 100 - t.index(q)
    matches = sum(1 for c in q if c in t)
    return int((matches / max(len(q), 1)) * 80)


def icon_from_name(icon_name):
    if not icon_name:
        return None
    if icon_name.startswith("/"):
        try:
            return Gio.FileIcon.new_for_path(icon_name)
        except Exception:
            return None
    theme = Gtk.IconTheme.get_default()
    if theme.has_icon(icon_name):
        return Gio.Icon.new_for_string(icon_name)
    return None


class LauncherWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Smart Search")
        self.set_default_size(620, 480)
        self.set_resizable(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("key-press-event", self.on_key_press)
        self.connect("focus-out-event", self.on_focus_out)

        self.apps = load_all_apps()
        self.filtered = list(self.apps)
        self.selected_index = 0

        self._build_ui()
        self._update_list()

    def _build_ui(self):
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(outer)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.set_margin_start(16)
        header.set_margin_end(16)
        header.set_margin_top(12)
        header.set_margin_bottom(8)
        outer.pack_start(header, False, False, 0)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_hexpand(True)
        self.search_entry.set_placeholder_text("Search...")
        self.search_entry.connect("search-changed", self.on_search_changed)
        self.search_entry.connect("key-press-event", self.on_entry_key_press)
        header.pack_start(self.search_entry, True, True, 0)

        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        outer.pack_start(separator, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(380)
        outer.pack_start(scroll, True, True, 0)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.listbox.connect("row-activated", self.on_row_activated)
        scroll.add(self.listbox)

        self.status_label = Gtk.Label()
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.set_margin_start(16)
        self.status_label.set_margin_top(4)
        self.status_label.set_margin_bottom(4)
        self.status_label.set_opacity(0.5)
        outer.pack_start(self.status_label, False, False, 0)

        self.show_all()
        GLib.idle_add(self.search_entry.grab_focus)

    def on_search_changed(self, entry):
        query = entry.get_text().strip()
        if not query:
            self.filtered = list(self.apps)
        else:
            scored = [(fuzzy_score(query, app["name"]), app) for app in self.apps]
            scored = [(s, a) for s, a in scored if s > 20]
            scored.sort(key=lambda x: x[0], reverse=True)
            self.filtered = [a for _, a in scored]

        self.selected_index = 0
        self._update_list()

    def _update_list(self):
        children = self.listbox.get_children()
        for child in children:
            self.listbox.remove(child)

        for i, app in enumerate(self.filtered):
            row = self._build_row(app, i)
            self.listbox.add(row)

        self.listbox.show_all()
        count = len(self.filtered)
        self.status_label.set_text(f"{count} app{'s' if count != 1 else ''} found")

    def _build_row(self, app, index):
        row = Gtk.ListBoxRow()
        row._app = app
        row._index = index
        row.set_activatable(True)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_valign(Gtk.Align.CENTER)

        icon_name = app.get("icon", "")
        icon_widget = None
        if icon_name:
            gio_icon = icon_from_name(icon_name)
            if gio_icon:
                icon_widget = Gtk.Image.new_from_gicon(gio_icon, Gtk.IconSize.DIALOG)
                icon_widget.set_pixel_size(36)
            else:
                icon_widget = Gtk.Image.new_from_icon_name("application-x-executable", Gtk.IconSize.DIALOG)
                icon_widget.set_pixel_size(36)
        else:
            icon_widget = Gtk.Image.new_from_icon_name("application-x-executable", Gtk.IconSize.DIALOG)
            icon_widget.set_pixel_size(36)

        icon_widget.set_margin_end(4)
        box.pack_start(icon_widget, False, False, 0)

        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

        name_label = Gtk.Label(xalign=0)
        name_label.set_markup(f'<span size="medium"><b>{GLib.markup_escape_text(app["name"])}</b></span>')
        name_label.set_ellipsize(Pango.EllipsizeMode.END)
        name_label.set_halign(Gtk.Align.START)
        name_label.get_style_context().add_class("app-name")
        text_box.pack_start(name_label, False, False, 0)

        if app.get("comment"):
            comment_label = Gtk.Label(xalign=0, label=app["comment"])
            comment_label.set_ellipsize(Pango.EllipsizeMode.END)
            comment_label.set_halign(Gtk.Align.START)
            comment_label.get_style_context().add_class("app-comment")
            text_box.pack_start(comment_label, False, False, 0)

        box.pack_start(text_box, True, True, 0)
        row.add(box)

        if index == self.selected_index:
            row.set_state_flags(Gtk.StateFlags.SELECTED, False)

        return row

    def on_row_activated(self, listbox, row):
        if row and hasattr(row, "_app"):
            launch_app(row._app["exec"])
            self.close()

    def on_key_press(self, widget, event):
        key = Gdk.keyval_name(event.keyval)

        if key == "Escape":
            self.close()
            return True

        if key == "Return":
            if self.filtered and 0 <= self.selected_index < len(self.filtered):
                launch_app(self.filtered[self.selected_index]["exec"])
                self.close()
            return True

        if key == "Down":
            if self.filtered:
                self.selected_index = min(self.selected_index + 1, len(self.filtered) - 1)
                self._update_selection()
            return True

        if key == "Up":
            if self.filtered:
                self.selected_index = max(self.selected_index - 1, 0)
                self._update_selection()
            return True

        return False

    def on_entry_key_press(self, widget, event):
        return self.on_key_press(widget, event)

    def _update_selection(self):
        rows = self.listbox.get_children()
        for i, row in enumerate(rows):
            if i == self.selected_index:
                row.set_state_flags(Gtk.StateFlags.SELECTED, False)
            else:
                row.unset_state_flags(Gtk.StateFlags.SELECTED)

        if rows and 0 <= self.selected_index < len(rows):
            rows[self.selected_index].grab_focus()

    def on_focus_out(self, widget, event):
        self.close()
        return True


def main():
    app = LauncherWindow()
    app.get_style_context().add_class("launcher-window")
    app.connect("destroy", Gtk.main_quit)
    Gtk.main()


if __name__ == "__main__":
    main()

