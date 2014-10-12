#!/usr/bin/python3
# -*- coding: utf-8 -*-

# kroppzeug: Helps you to manage your server kindergarten!
#
# Copyright 2012-2014 Dan Luedtke <mail@danrl.de>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import string
import os
import time
import sys
import signal
from subprocess import call
from socket import gethostname

# global variables
host_groups     = {}
whereami        = False
ssh_config_file = os.getenv("HOME") + '/.ssh/config'
error_message   = ''
default_group   = 'none'
default_cmd     = 'ssh'

# Kroppzeug options
kropp_group     = '#kroppzeug_group'
kropp_ssh       = '#kroppzeug_ssh'
kropp_desc      = '#kroppzeug_description'
kropp_update    = '#kroppzeug_update'
kropp_autocmd   = '#kroppzeug_autocmd'
kropp_managed   = '#kroppzeug_managed'

# colors, control sequences
TERM_RED        = '\033[91m'
TERM_GREEN      = '\033[92m'
TERM_YELLOW     = '\033[93m'
TERM_BLUE       = '\033[94m'
TERM_MAGENTA    = '\033[95m'
TERM_BOLD       = '\033[1m'
TERM_RESET      = '\033[0m'


# catch SIGINT (e.g. ctrl+c)
def signal_handler(signal, frame):
    print()
    print(TERM_RESET + 'Life tasted so good, dude!')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


# get terminal size
def get_termsize():
    y, x = os.popen('stty size', 'r').read().split()
    y = int(y)
    x = int(x)
    return y, x


# read ssh hosts from config file
def parse_hosts(filename):
    i = -1
    inputfile = open(filename, 'r')
    for line in inputfile.readlines():
        # strip whitespaces
        line = line.strip()
        # extract options
        line = line.split(None, 1)
        # parse options
        if len(line) < 2:
            continue
        option = line[0]
        value = line[1]
        if option.lower() == 'host':
            shortcut = value
            about = 'no description'
            update = False
            autocmd = False
            shell = default_cmd
            group = default_group
            i += 1
        elif option.lower() == kropp_group and value.lower() != default_group:
            group = value
        elif option.lower() == kropp_ssh and value.lower() != default_cmd:
            shell = value
        elif option.lower() == kropp_desc:
            about = value
        elif option.lower() == kropp_update and len(value) > 0:
            update = value
        elif option.lower() == kropp_autocmd and value.lower() != 'false':
            autocmd = value
        elif option.lower() == kropp_managed and value.lower() == 'true':
            # fill the dictionary with the parsed stuff
            try:
                hosts_list = host_groups[group]
                hosts_list.append([shortcut, about, update, autocmd, shell])
            except KeyError:
                host_groups[group] = [[shortcut, about, update, autocmd, shell]]
    inputfile.close()


# print header
def print_header(terminal_size_x):
    os.system('clear')
    print(TERM_BOLD + TERM_RED, end='')
    if whereami is True:
        print()
        print(gethostname().center(terminal_size_x))
        print()
    else:
        print('┬┌─┬─┐┌─┐┌─┐┌─┐┌─┐┌─┐┬ ┬┌─┐'.center(terminal_size_x))
        print('├┴┐├┬┘│ │├─┘├─┘┌─┘├┤ │ ││ ┬'.center(terminal_size_x))
        print('┴ ┴┴└─└─┘┴  ┴  └─┘└─┘└─┘└─┘'.center(terminal_size_x))
    print(TERM_GREEN + '─' * terminal_size_x)


# print a list of available hosts
def print_hosts(shortcut_width, about_width, terminal_size_x):
    # get the keys as a sorted list
    group_keys = sorted(host_groups.keys())
    # if default group is used or not and if so
    if default_group in group_keys:
        group_keys.remove(default_group)
        # insert at the beginning
        group_keys.insert(0, default_group)
    # iterate through groups
    for group_key in group_keys:
        if group_key != default_group:
            group_label = '─| ' + TERM_BOLD + TERM_MAGENTA + group_key + TERM_RESET + ' |'
            group_label = group_label + '─' * (terminal_size_x - len(group_key) - 5)
            print(group_label.center(terminal_size_x))
        # empty line
        print()
        host_group = host_groups[group_key]
        i = -1
        for host in host_group:
            i += 1
            host_shortcut = host[0][:shortcut_width]
            if host[1] is not False:
                host_about = ' ' + host[1][:about_width] + ' '
            else:
                host_about = ' '
            out = ' '
            out = out + TERM_BOLD + TERM_BLUE + host_shortcut.rjust(shortcut_width)
            out = out + TERM_RESET + host_about.ljust(about_width)
            if i % 2 == 0:
                print(out, end='')
            else:
                print(out)
            if len(host_group) == i + 1 and len(host_group) % 2 != 0:
                print()
        # empty line
        print()


def print_vertical_space(term_size_y, lines_to_spare=2):
    # position
    posx = str(term_size_y - lines_to_spare)
    print('\033[' + posx + ';0f')


def print_horizontal_line(term_size_x):
    # horizontal line
    print(TERM_BOLD + TERM_GREEN + '─' * term_size_x + TERM_RESET)


def print_rest_screen(term_size_y, term_size_x):
    global error_message
    if error_message == '':
        print_vertical_space(term_size_y)
        print_horizontal_line(term_size_x)
    else:
        print_vertical_space(term_size_y, 3)
        print_horizontal_line(term_size_x)
        print(TERM_BOLD + TERM_RED + error_message + TERM_RESET)
        # reset error message
        error_message = ''


def build_screen():
    # build screen
    # terminal dimensions and sizes
    term_size_y, term_size_x = get_termsize()
    # fine grained layouting
    # bss,shortcut_width,bs,about_width,aas,ms
    bss = 1     # before_shortcut_space
    sw  = 16    # shortcut_width
    bs  = 1     # between_space
    aas = 1     # after_about_space
    ms  = 0     # middle_space
    nc  = 2     # number of columns
    shortcut_width = sw
    about_width = (term_size_x - ((((bss + sw + bs + aas) * nc) + ms))) // nc
    # print the actual screen
    print_header(term_size_x)
    print_hosts(shortcut_width, about_width, term_size_x)
    print_rest_screen(term_size_y, term_size_x)


def connect_host(host):
    auto_command = host[3]
    shortcut = host[0]
    # craft shell command
    shell_command = host[4] + ' ' + shortcut
    if auto_command is not False:
        shell_command += ' -t "' + auto_command + '"'
    # go!
    os.system('clear')
    print(TERM_YELLOW + shell_command + TERM_RESET)
    call(shell_command, shell=True)


def update_host(host):
    update_command = host[2]
    shortcut = host[0]
    # craft shell command
    shell_command = 'ssh -v ' + shortcut
    if update_command is not False:
        shell_command += ' -t "' + update_command + '"'
        # go!
        os.system('clear')
        print(TERM_YELLOW + shell_command + TERM_RESET)
        call(shell_command, shell=True)


def get_host_for_shortcut(shortcut):
    # travers through dictionary entries
    for key_value_pair in host_groups.items():
        # access the values which are lists of hosts
        # and the value is a single host
        for host in key_value_pair[1]:
            if host[0] == shortcut:
                return host
    # if nothing is found return False
    return False


def hosts_startswith(text):
    result_list = []
    # travers through dictionary entries
    for key_value_pair in host_groups.items():
        # access the values which are lists of hosts
        # and the value is a single host
        for host in key_value_pair[1]:
            if host[0].startswith(text):
                result_list.append(host[0])
    return result_list


def groups_startswith(text):
    groups = host_groups.keys()
    return [host for host in groups if host.startswith(text)]

parse_hosts(ssh_config_file)


import cmd


class KroppzeugShell(cmd.Cmd):
    prompt = TERM_BOLD + TERM_YELLOW + '(kroppzeug)$ ' + TERM_RESET

    def __init__(self):
        super(KroppzeugShell, self).__init__()

    #--------------commands---------------#
    def do_whereami(self, arg):
        'Toggle if current hostname sould be displayed instead of the '\
        'Kroppzeug title\ntype it again to switch back: whereami'
        global whereami
        if whereami is True:
            whereami = False
        else:
            whereami = True

    def do_connect(self, arg):
        'Connect to specified host: connect valkyr'
        global error_message
        host = get_host_for_shortcut(arg)
        if host is not False:
            connect_host(host)
            time.sleep(1)
        else:
            error_message = 'unknown/undefined shortcut'

    def do_update(self, arg):
        'Update specified host: update painkiller \n' \
        'Update all hosts:      update all '
        global error_message
        term_size_y, term_size_x = get_termsize()
        if arg == 'all':
            # travers through dictionary entries
            for key_value_pair in host_groups.items():
                # access the values which are lists of hosts
                # and the value is a single host
                for host in key_value_pair[1]:
                    update_host(host)
                    print(TERM_BOLD + TERM_GREEN + '─' * term_size_x + TERM_RESET)
                    time.sleep(1)
        else:
            host = get_host_for_shortcut(arg)
            if host is not False:
                update_host(host)
                print(TERM_BOLD + TERM_GREEN + '─' * term_size_x + TERM_RESET)
                time.sleep(3)
            else:
                error_message = 'unknown/undefined shortcut'

    def do_update_group(self, arg):
        'Update specified group: update_group work'
        global error_message
        term_size_y, term_size_x = get_termsize()
        try:
            hosts_list = host_groups[arg]
            for host in hosts_list:
                update_host(host)
                print(TERM_BOLD + TERM_GREEN + '─' * term_size_x + TERM_RESET)
                time.sleep(1)
        except KeyError:
            error_message = 'unknown/undefined shortcut'

    def do_list(self, arg):
        'List all available shortcuts for managed hosts: list'
        build_screen()

    def do_exit(self, arg):
        'Exit/quit the Kroppzeug shell: exit'
        global error_message
        error_message = 'Thank you for using Kroppzeug to manage your digital offspring!'
        return True

    #--------------tab completion---------------#
    def complete_connect(self, text, line, begidx, endidx):
        return hosts_startswith(text)

    def complete_update(self, text, line, begidx, endidx):
        result = hosts_startswith(text)
        if text == '' or 'all'.startswith(text):
            result.append('all')
        return result

    def complete_update_group(self, text, line, begidx, endidx):
        return groups_startswith(text)

    #------------aux cmd functions-------------#
    # if empty line is submitted do nothing just rebuild screen
    def emptyline(self):
        global error_message
        error_message = 'empty line/command, nothing to do!'
        pass

    # if no matching method for command is found do nothing just rebuild screen
    def default(self, arg):
        global error_message
        error_message = 'unknown/undefined command'
        pass

    # initial draw of screen befor command loop
    def preloop(self):
        build_screen()

    def postcmd(self, stop, line):
        if not line.startswith('help'):
            build_screen()
        return stop

if __name__ == '__main__':
    KroppzeugShell().cmdloop()
