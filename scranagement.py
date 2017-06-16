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

    p = configargparse.ArgParser(default_config_files=[default_conf])

    p.add("-c", required=False, is_config_file=True, metavar="file",
          help="config file location, defaults to %s" % default_conf)
    p.add("-n", required=False, type=int, default=default_n, metavar="count",
          help="the latest N files to list, defaults to %d" % default_n)
    p.add("-d", required=True, metavar="dir", help="the screenshot directory")
    p.add("--save", required=False, action="store_true",
          help="if specified, saves the current configuration to the config file")

    opts = vars(p.parse_args())

    # remove unneeded option
    opts.pop("conf", None)

    # save to config file
    if opts.pop("save"):
        cp = configparser.ConfigParser()
        cp.read_dict({"settings": opts})
        with open(default_conf, "w") as f:
            cp.write(f)
        debug("Wrote config to %s" % default_conf)
        sys.exit(0)  # TODO return success-and-dont-continue exit code

    return Config(directory=_expand_path(opts["directory"]), latest_n=opts["latest"])


if __name__ == "__main__":
    res = main(parse_args())
    exit = 0 if res else 2
    sys.exit(exit)
