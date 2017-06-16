#!/usr/bin/env python3

import os
import glob
import sys
from collections import namedtuple
from enum import Enum

import configargparse
import configparser


class Action(Enum):
    SAVE_CONFIG = 0
    SYMLINKS = 1
    GET = 2


Config = namedtuple(
    "Config", ["config", "dir", "count", "action", "symlink_dir", "symlink_format"])


def _expand_path(path):
    return os.path.expanduser(os.path.expandvars(path))


def debug(msg):
    print(msg, file=sys.stderr)


def get_n_latest(directory, n):
    # TODO check for missing directory
    files = [os.path.abspath(f) for f in glob.glob("%s/*" % directory) if os.path.isfile(f)]
    files.sort(key=os.path.getmtime, reverse=True)
    return files[:n]


def handler_get_n_latest(conf):
    files = get_n_latest(conf.dir, conf.count)

    # none found
    if not files:
        return False

    for f in files:
        print(f)

    # TODO err codes
    return True


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
    return True


def handler_update_symlinks(conf):
    # TODO
    debug("Updating symlinks")


def parse_args():
    default_conf = _expand_path("$XDG_CONFIG_HOME/scranagement.conf")
    # TODO choose $HOME if $XDG_CONFIG_HOME doesnt exist
    default_n = 1
    default_format = "screenshot-latest-%%(n)"
    # TODO accept date formatting too?

    p = configargparse.ArgParser(default_config_files=[default_conf])
    # TODO add examples in epilog using RawDescriptionHelpFormatter

    p.add("-c", "--config", is_config_file=True, metavar="FILE",
          help="config file location, defaults to %s" % default_conf)  # TODO dont expand default
    p.add("--save", action="store_true",
          help="if specified, saves the current configuration to the config file")
    p.add("-d", "--dir", required=True, metavar="DIR",
          help="the screenshot directory")
    p.add("-n", "--count", type=int, default=default_n, metavar="COUNT",
          help="the latest n screenshots to list, defaults to %d" % default_n)

    p.add("-u", "--update-symlinks", action="store_true", dest="update-symlinks",
          help="create symlinks to the latest n screenshots")
    p.add("-s", "--symlink-dir", metavar="DIR", dest="symlink-dir",
          help="the directory to create symlinks in, defaults to the screenshot directory")
    p.add("-f", "--symlink-format", default=default_format, metavar="FORMAT", dest="symlink-format",
          help="the format string for symlinks, where %%(n) is the order index")

    opts = vars(p.parse_args())

    # set default
    if not opts["symlink-dir"]:
        opts["symlink-dir"] = opts["dir"]
    if not opts["config"]:
        opts["config"] = default_conf

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
        # uh oh
        debug("Error: only one of --update-symlinks and --save can be specified")
        sys.exit(1)  # TODO return error code instead of exit

    return Config(
        config=opts["config"],
        dir=_expand_path(opts["dir"]),
        count=opts["count"],
        action=action,
        symlink_dir=opts["symlink-dir"],
        symlink_format=opts["symlink-format"])


ACTION_HANDLERS = [
    handler_save_config,
    handler_update_symlinks,
    handler_get_n_latest
]

if __name__ == "__main__":
    conf = parse_args()
    res = ACTION_HANDLERS[conf.action.value](conf)

    exit = 0 if res else 2
    sys.exit(exit)
