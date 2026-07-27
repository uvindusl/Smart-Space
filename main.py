import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
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

def main():
    win = Window()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
