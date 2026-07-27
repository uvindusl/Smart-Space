import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from pathlib import Path
import configparser


# application directries
directories = [
    Path("/usr/share/applications"),
    Path.home() / ".local/share/applications",
]

def get_application_with_metadata(filepath):
    config = configparser.ConfigParser(interpolation=None)
    config.read(filepath, encoding="utf-8")

    if not config.has_section("Desktop Entry"):
        return None

    entry = config["Desktop Entry"]

    # Only include Application types (skip Link, Directory, etc.)
    if entry.get("Type") != "Application":
        return None

    # Skip apps marked as hidden from launchers
    if entry.get("NoDisplay", "false").lower() == "true":
        return None

    name = entry.get("Name", "")
    if not name:
        return None

    comment = entry.get("Comment", "")
    exec_cmd = entry.get("Exec", "")
    icon = entry.get("Icon", "")

    categories = entry.get("Categories", "")

    return {
        "name": name,
        "comment": comment,
        "exec": exec_cmd,
        "icon": icon,
        "categories": categories,
        "file": str(filepath),
    }

def load_apps():
    apps = []
    seen = set()

    for desktop_dir in directories:
        for filepath in desktop_dir.glob("*.desktop"):
            app = get_application_with_metadata(filepath)
            if app and app["name"] not in seen:
                seen.add(app["name"])
                apps.append(app)

    apps.sort(key=lambda a: a["name"].lower())
    return apps

# apps as list 
apps = load_apps()

# main window
class Window(Gtk.Window):
    def __init__(self):
        super().__init__(title="Smart Space")
        self.set_default_size(620, 480)
        self.set_resizable(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.app_list = apps 
        self.selected_index = 0

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
        self.search_entry.connect("search-changed", self._on_filter_apps)
        header.pack_start(self.search_entry, True, True, 0)

        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        outer.pack_start(separator, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(380)
        outer.pack_start(scroll, True, True, 0)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scroll.add(self.listbox)

        self.status_label = Gtk.Label()
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.set_margin_start(16)
        self.status_label.set_margin_top(4)
        self.status_label.set_margin_bottom(4)
        self.status_label.set_opacity(0.5)
        outer.pack_start(self.status_label, False, False, 0)

        self._populate_list()

        self.show_all()
        GLib.idle_add(self.search_entry.grab_focus)

    # populate the list 
    def _populate_list(self):
        for child in self.listbox.get_children():
            self.listbox.remove(child)

        for i, app in enumerate(self.app_list):
            row = self._build_row(app, i)
            self.listbox.add(row)

        self.listbox.show_all()
        count = len(self.app_list)
        self.status_label.set_text(f"{count} app{'s' if count != 1 else ''} found")

    # build the row
    def _build_row(self, app, index):
        row = Gtk.ListBoxRow()
        row._app = app
        row._index = index
        row.set_activatable(True)

        label = Gtk.Label(xalign=0)
        label.set_text(app["name"])
        label.set_halign(Gtk.Align.START)
        label.set_margin_start(8)
        label.set_margin_end(8)
        label.set_margin_top(4)
        label.set_margin_bottom(4)
        row.add(label)

        if index == self.selected_index:
            row.set_state_flags(Gtk.StateFlags.SELECTED, False)

        return row

    def _on_filter_apps(self, entry):
        query = entry.get_text().lower()
        self.app_list = [a for a in apps if query in a["name"].lower()]
        self._populate_list()


def main():
    win = Window()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()

if __name__ == "__main__":
    main()
