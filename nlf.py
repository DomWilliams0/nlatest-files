#!/usr/bin/env python3

import os
import glob
import sys
from collections import namedtuple
from enum import Enum

import configargparse
import configparser


class NLFError(Exception):
    def __init__(self, msg):
        self.msg = msg


class DirectoryError(NLFError):
    pass


class ConfigurationError(NLFError):
    pass


class Action(Enum):
    SAVE_CONFIG = 0
    SYMLINKS = 1
    GET = 2


QUIET = False


Config = namedtuple(
    "Config", ["config", "dir", "count", "action", "symlink_dir", "symlink_format"])


def _expand_path(path):
    return os.path.expanduser(os.path.expandvars(path))


def debug(msg):
    if not QUIET:
        print(msg, file=sys.stderr)


def get_n_latest(directory, n):
    if not os.path.exists(directory):
        raise DirectoryError("Directory not found")
    if not os.path.isdir(directory):
        raise DirectoryError("Given path is not a directory")

    files = [os.path.abspath(f) for f in glob.glob(
        "%s/*" % directory) if os.path.isfile(f) and not os.path.islink(f)]

    if len(files) == 0:
        raise DirectoryError("No files found")

    files.sort(key=os.path.getmtime, reverse=True)
    return files[:n]


def handler_get_n_latest(conf):
    files = get_n_latest(conf.dir, conf.count)
    for f in files:
        print(f)


def handler_save_config(conf):
    cp = configparser.ConfigParser()

    # split up settings
    general_settings, symlink_settings = {}, {}
    for (k, v) in conf._asdict().items():
        if k.startswith("symlink_"):
            section = symlink_settings
        elif k in ["dir", "count"]:
            section = general_settings
        else:
            continue

        section[k.replace("_", "-")] = v

    cp.read_dict({"general": general_settings,
                  "symlinks": symlink_settings})
    with open(conf.config, "w") as f:
        cp.write(f)

    debug("Wrote config to %s" % conf.config)


def update_symlinks(sym_dir, format, source_dir, n):
    if n != 1 and not "{n}" in format:
        raise ConfigurationError("Missing {n} in symlink format")

    files = get_n_latest(source_dir, n)

    # TODO special format for the first

    # delete all existing
    delete_glob = format.format(n="*")
    count = 0
    for sym in glob.glob(os.path.join(sym_dir, delete_glob)):
        if os.path.islink:
            os.remove(sym)
            count += 1
    debug("Removed %d existing symlink(s)" % count)

    for (i, scr) in enumerate(files):
        sym = os.path.join(sym_dir, format.format(n=i + 1))
        debug("Creating symlink %s -> %s" % (os.path.basename(scr), sym))
        os.symlink(scr, sym)


def handler_update_symlinks(conf):
    update_symlinks(conf.symlink_dir, conf.symlink_format,
                    conf.dir, conf.count)


def parse_args():
    def positive_int(val):
        i = int(val)
        if i <= 0:
            raise configargparse.ArgumentTypeError("Positive integer expected")
        return i

    default_conf_raw = "$XDG_CONFIG_HOME/nlatest-files.conf"
    default_conf = _expand_path(default_conf_raw)
    default_n = 1
    default_format = "latest-{n}"
    prog = "nlf"

    p = configargparse.ArgParser(default_config_files=[default_conf], prog=prog,
                                 formatter_class=configargparse.RawDescriptionHelpFormatter,
                                 epilog="""
EXAMPLES
{prog} -d ~/invoices -n 5
    Prints the latest 5 files in ~/invoices

{prog} -d ~/invoices -n 5 --save
    Saves the given parameters to the default config file

{prog} -d ~/invoices -n 5 -c ~/dotfiles/myconfig.conf --save
    Saves the given parameters to the specified config file

{prog}
    Prints the latest 5 again, using from the config file

{prog} -u -s $HOME/screenshots -f "screeny-{{n}}" -n 3
    Creates symlinks to the top 3 latest screenshots in ~/screenshots

scrot -e 'mv -u $f ~/screenshots/ && {prog} -u -d ~/screenshots -n 1 -f "latest"'
    Takes a screenshot with scrot, moves it to ~/screenshots, then
    adds a `symlink ~/screenshots/latest` pointing to it

            """.format(prog=prog))

    p.add("-c", "--config", is_config_file=True, metavar="FILE",
          help="config file location, defaults to %s" % default_conf_raw)
    p.add("--save", action="store_true",
          help="if specified, saves the current configuration to the config file")
    p.add("-d", "--dir", required=True, metavar="DIR",
          help="the source directory")
    p.add("-n", "--count", type=positive_int, default=default_n, metavar="COUNT",
          help="the latest n files to list, defaults to %d" % default_n)

    p.add("-u", "--update-symlinks", action="store_true", dest="update-symlinks",
          help="create symlinks to the latest n files")
    p.add("-s", "--symlink-dir", metavar="DIR", dest="symlink-dir",
          help="the directory to create symlinks in, defaults to the source directory")
    p.add("-f", "--symlink-format", default=default_format, metavar="FORMAT", dest="symlink-format",
          help="the format string for symlinks, where {n} is the order index, defaults to '%s'. {n} must be included, unless n = 1" % default_format)
    p.add("-q", "--quiet", action="store_true",
          help="if specified, no status messages will be printed to stderr")

    opts = vars(p.parse_args())

    # set default
    if not opts["symlink-dir"]:
        opts["symlink-dir"] = opts["dir"]
    if not opts["config"]:
        opts["config"] = default_conf

    # set global
    global QUIET
    QUIET = opts["quiet"]

    # determine action
    actions = [opts["save"], opts["update-symlinks"]]
    action_sum = sum(actions)
    if action_sum == 0:
        # default
        action = Action.GET
    elif action_sum == 1:
        # one was chosen
        action = Action(actions.index(True))
    else:
        raise ConfigurationError(
            "Only one of --update-symlinks and --save can be specified")

    return Config(
        config=opts["config"],
        dir=_expand_path(opts["dir"]),
        count=opts["count"],
        action=action,
        symlink_dir=opts["symlink-dir"],
        symlink_format=opts["symlink-format"]
    )


ACTION_HANDLERS = [
    handler_save_config,
    handler_update_symlinks,
    handler_get_n_latest
]

def main():
    try:
        conf = parse_args()
        ACTION_HANDLERS[conf.action.value](conf)
        exit = 0
    except NLFError as e:
        debug("%s: %s" % (e.__class__.__name__, e.msg))
        exit = 1

    sys.exit(exit)

if __name__ == "__main__":
    main()
