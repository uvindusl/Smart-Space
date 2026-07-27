import configparser
import subprocess
from pathlib import Path

def get_desktop_dirs():
    dirs = []
    sys_dir = Path("/usr/share/applications")
    if sys_dir.is_dir():
        dirs.append(sys_dir)
    local_dir = Path.home() / ".local" / "share" / "applications"
    if local_dir.is_dir():
        dirs.append(local_dir)
    return dirs


def parse_desktop_file(filepath):
    config = configparser.ConfigParser(interpolation=None)
    config.read(filepath, encoding="utf-8")

    if not config.has_section("Desktop Entry"):
        return None

    entry = config["Desktop Entry"]

    if entry.get("Type") != "Application":
        return None

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


def load_all_apps():
    apps = []
    seen = set()

    for desktop_dir in get_desktop_dirs():
        for filepath in desktop_dir.glob("*.desktop"):
            app = parse_desktop_file(filepath)
            if app and app["name"] not in seen:
                seen.add(app["name"])
                apps.append(app)

    apps.sort(key=lambda a: a["name"].lower())
    return apps


def launch_app(exec_cmd):

    cmd = exec_cmd.replace("%f", "").replace("%F", "")
    cmd = cmd.replace("%u", "").replace("%U", "")
    cmd = cmd.replace("%d", "").replace("%D", "")
    cmd = cmd.replace("%n", "").replace("%N", "")
    cmd = cmd.replace("%i", "").replace("%c", "")
    cmd = cmd.replace("%k", "").strip()

    try:
        subprocess.Popen(cmd, shell=True, start_new_session=True)
        return True
    except Exception:
        return False
