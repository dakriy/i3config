#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script is a simple wrapper which prefixes each i3status line with custom
# information. It is a python reimplementation of:
# http://code.stapelberg.de/git/i3status/tree/contrib/wrapper.pl
#
# To use it, ensure your ~/.i3status.conf contains this line:
#     output_format = "i3bar"
# in the 'general' section.
# Then, in your ~/.i3/config, use:
#     status_command i3status | ~/i3status/contrib/wrapper.py
# In the 'bar' section.2
#
# In its current version it will display the cpu frequency governor, but you
# are free to change it to display whatever you like, see the comment in the
# source code below.
#
# © 2012 Valentin Haenel <valentin.haenel@gmx.de>
#
# This program is free software. It comes without any warranty, to the extent
# permitted by applicable law. You can redistribute it and/or modify it under
# the terms of the Do What The Fuck You Want To Public License (WTFPL), Version
# 2, as published by Sam Hocevar. See http://sam.zoy.org/wtfpl/COPYING for more
# details.

import sys
import json
import subprocess
from pycmus import remote
import pathlib
import time


def get_gpu():
    """ Get the current gpu """
    # with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor') as fp:
    #     return fp.readlines()[0].strip()
    output = subprocess.run(['optimus-manager', '--status'], stdout=subprocess.PIPE)
    gpu = output.stdout.decode('utf-8').split('\n')[3].split(' : ')[1]
    return gpu


def print_line(message):
    """ Non-buffered printing to stdout. """
    sys.stdout.write(message + '\n')
    sys.stdout.flush()


def read_line():
    """ Interrupted respecting reader for stdin. """
    # try reading a line, removing any extra whitespace
    try:
        line = sys.stdin.readline().strip()
        # i3status sends EOF, or an empty line
        if not line:
            sys.exit(3)
        return line
    # exit on ctrl-c
    except KeyboardInterrupt:
        sys.exit()


def convert_seconds_to_sane_time(seconds: int):
    time = seconds
    hours = int(time / 3600)
    time -= hours * 3600
    minutes = int(time / 60)
    time -= minutes * 60
    seconds = time
    if hours > 0:
        return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
    else:
        return '{:02d}:{:02d}'.format(minutes, seconds)


def get_cmus_status():
    try:
        cmus = remote.PyCmus()
        dict = cmus.get_status_dict()
        status = dict['status']
        if status == 'playing' or status == 'paused':
            return '{} ({} {} / {})'.format(pathlib.Path(dict['file']).stem, status,
                                            convert_seconds_to_sane_time(int(dict['position'])),
                                            convert_seconds_to_sane_time(int(dict['duration'])))
        else:
            return status
    except FileNotFoundError:
        return 'not running'


if __name__ == '__main__':
    # Skip the first line which contains the version header.
    print_line(read_line())

    # The second line contains the start of the infinite array.
    print_line(read_line())

    # Only need to get GPU once as the whole x server has to restart when changing the GPU
    gpu = get_gpu()

    music = get_cmus_status()
    last = time.time()

    while True:
        line, prefix = read_line(), ''
        # ignore comma at start of lines
        if line.startswith(','):
            line, prefix = line[1:], ','

        j = json.loads(line)

        # only update music at most every 4 seconds as it takes
        # a while and can crash if hit to quickly, also it lags
        # behind
        current = time.time()
        if current - last > 4:
            music = get_cmus_status()
            last = current

        # insert information into the start of the json, but could be anywhere
        # CHANGE THIS LINE TO INSERT SOMETHING ELSE
        j.insert(0, {'full_text': 'GPU: %s' % gpu, 'name': 'GPU'})
        j.insert(0, {'full_text': 'Music: %s' % music, 'name': 'music'})
        # and echo back new encoded json
        print_line(prefix + json.dumps(j))
