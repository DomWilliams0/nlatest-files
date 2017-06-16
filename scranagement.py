#!/usr/bin/env python3

import os
import glob
import sys
from collections import namedtuple

Config = namedtuple('Config', ['directory', 'latest_n'])


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


def parse_args():
    # TODO parse from args
    directory = "$HOME/screenshots"
    n = 3
    return (True, Config(directory=_expand_path(directory), latest_n=n))


def show_usage():
    print("Usage: X")  # TODO


if __name__ == "__main__":
    (success, conf) = parse_args()
    if not success:
        show_usage()
        sys.exit(1)

    res = main(conf)
    exit = 0 if res else 2
    sys.exit(exit)
