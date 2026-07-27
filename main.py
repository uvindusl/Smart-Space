import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from rapidfuzz import fuzz

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

        self.show_all()
        GLib.idle_add(self.search_entry.grab_focus)

def main():
    win = Window()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
