#!/usr/bin/env python3

import os
import glob
import sys
from collections import namedtuple

import configargparse
import configparser

Config = namedtuple("Config", ["directory", "latest_n"])


def get_n_latest(directory, n):
    # TODO check for missing directory
    files = [f for f in glob.glob("%s/*" % directory) if os.path.isfile(f)]
    files.sort(key=os.path.getmtime, reverse=True)
    return files[:n]


def main(conf):
    files = get_n_latest(conf.directory, conf.latest_n)

    # none found
    if not files:
        return False

    for f in files:
        print(os.path.abspath(f))

    # TODO err codes
    return True


def _expand_path(path):
    return os.path.expanduser(os.path.expandvars(path))


def debug(msg):
    print(msg, file=sys.stderr)


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

    p.add("-u", "--update-symlinks", action="store_true",
          help="create symlinks to the latest n screenshots")
    p.add("-s", "--symlink-dir", metavar="DIR", dest="symlink-dir",
          help="the directory to create symlinks in, defaults to the screenshot directory")
    p.add("-f", "--symlink-format", default=default_format, metavar="FORMAT", dest="symlink-format",
          help="the format string for symlinks, where %%(n) is the order index")

    opts = vars(p.parse_args())

    # set default
    if not opts["symlink-dir"]:
        opts["symlink-dir"] = opts["dir"]

    # save to config file
    if opts["save"]:
        cp = configparser.ConfigParser()

        # splt up settings
        general_settings, symlink_settings = {}, {}
        for (k, v) in opts.items():
            if k.startswith("symlink-"):
                section = symlink_settings
            elif k in ["dir", "count"]:
                section = general_settings
            else:
                continue

            section[k] = v

        cp.read_dict({"general": general_settings,
                      "symlinks": symlink_settings})
        with open(default_conf, "w") as f:
            cp.write(f)

        debug("Wrote config to %s" % default_conf)
        sys.exit(0)  # TODO return action with what to do

    return Config(directory=_expand_path(opts["dir"]), latest_n=opts["count"])


if __name__ == "__main__":
    res = main(parse_args())
    exit = 0 if res else 2
    sys.exit(exit)
