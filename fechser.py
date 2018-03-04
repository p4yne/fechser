#!/usr/bin/python3
# -*- coding: utf-8 -*-

# fechser: Helps you to manage your server kindergarten!
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

import os
import time
import sys
import signal
import cmd
from subprocess import call
from socket import gethostname

# global variables
host_groups     = {}
hostname        = False
ssh_config_file = os.getenv("HOME") + '/.ssh/config'
error_message   = ''
default_group   = 'none'
default_cmd     = 'ssh'
default_no_desc = 'no description'

# Kroppzeug options
kf_group     = '#kf_group'
kf_ssh       = '#kf_ssh'
kf_desc      = '#kf_description'
kf_update    = '#kf_update'
kf_autocmd   = '#kf_autocmd'
kf_managed   = '#kf_managed'

# colors, control sequences
TERM_RED        = '\033[91m'
TERM_GREEN      = '\033[92m'
TERM_YELLOW     = '\033[93m'
TERM_BLUE       = '\033[94m'
TERM_MAGENTA    = '\033[95m'
TERM_BOLD       = '\033[1m'
TERM_RESET      = '\033[0m'

#import codecs

#If encoding is old or broken on your system:
#if sys.stdout.encoding is None or sys.stdout.encoding == 'ANSI_X3.4-1968':
#    utf8_writer = codecs.getwriter('UTF-8')
#    if sys.version_info.major < 3:
#        sys.stdout = utf8_writer(sys.stdout, errors='replace')
#    else:
#        sys.stdout = utf8_writer(sys.stdout.buffer, errors='replace')


# catch SIGINT (e.g. ctrl+c)
def signal_handler(signal, frame):
    print()
    print(TERM_RESET + 'Life tasted so good, dude!')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


# get terminal size
def get_termsize():
    y, x = os.popen('stty size', 'r').read().split()
    return int(x), int(y)


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
            about = default_no_desc
            update = False
            autocmd = False
            shell = default_cmd
            group = default_group
            i += 1
        elif option.lower() == kf_group and value.lower() != default_group:
            group = value
        elif option.lower() == kf_ssh and value.lower() != default_cmd:
            shell = value
        elif option.lower() == kf_desc:
            about = value
        elif option.lower() == kf_update and len(value) > 0:
            update = value
        elif option.lower() == kf_autocmd and value.lower() != 'false':
            autocmd = value
        elif option.lower() == kf_managed and value.lower() == 'true':
            # fill the dictionary with the parsed stuff
            try:
                hosts_list = host_groups[group]
                hosts_list.append([shortcut, about, update, autocmd, shell])
            except KeyError:
                host_groups[group] = [[shortcut, about, update, autocmd, shell]]
    inputfile.close()


# print header
def print_header():
    global hostname
    termx, termy = get_termsize()
    os.system('clear')
    print(TERM_BOLD + TERM_RED, end='')
    if hostname is True:
        print(gethostname().center(termx))
    else:
        print('┌─┐┌─┐┌─┐┬ ┬┌─┐┌─┐┬─┐'.center(termx))
        print('├┤ ├┤ │  ├─┤└─┐├┤ ├┬┘'.center(termx))
        print('└  └─┘└─┘┴ ┴└─┘└─┘┴└─'.center(termx))
    print(TERM_GREEN + '─' * termx)


# print group identifier
def print_group_id(group_key):
    termx, termy = get_termsize()
    group_label = '─| ' + TERM_BOLD + TERM_MAGENTA + group_key + TERM_RESET + ' |'
    group_label = group_label + '─' * (termx - len(group_key) - 5)
    print(group_label.center(termx))


# print a list of available hosts
def print_hosts():
    termx, termy = get_termsize()

    # column length
    cwidth = 40
    # amount of columns
    camount = termx // cwidth
    # minimum 2 column layout
    # if camount == 1 then shrink dwidth
    if camount == 1:
        camount = 2
    # shortcut length
    swidth = 16
    # description length
    dwidth = (termx - ((swidth + 3) * camount)) // camount

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
            print_group_id(group_key)
        host_group = host_groups[group_key]
        i = 0 
        for host in host_group:
            i += 1
            host_shortcut = host[0][:swidth]
            if host[1] is not False:
                host_about = ' ' + host[1][:dwidth] + ' '
            else:
                host_about = ' '
            out = ' '
            out = out + TERM_BOLD + TERM_BLUE + host_shortcut.rjust(swidth)
            out = out + TERM_RESET + host_about.ljust(dwidth)
            if i % camount == 0:
               print(out)
            else:
                print(out, end='')
            if len(host_group) == i and len(host_group) % camount != 0:
                print()
    # empty line
    print()


# print vertical space
def print_vspace(lines_to_spare=2):
    termx, termy = get_termsize()
    # position
    posx = str(termy - lines_to_spare)
    print('\033[' + posx + ';0f')


# print horizontal line
def print_hline():
    termx, termy = get_termsize()
    print(TERM_BOLD + TERM_GREEN + '─' * termx + TERM_RESET)


# print the rest of the screen
def print_rest_screen():
    global error_message
    termx, termy = get_termsize()
    if error_message == '':
        print_vspace()
        print_hline()
    else:
        print_vspace(3)
        print_hline()
        print(TERM_BOLD + TERM_RED + error_message + TERM_RESET)
        # reset error message
        error_message = ''


# build the whole screen
def build_screen():
    print_header()
    print_hosts()
    print_rest_screen()


# connect to specified host
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


# update specified host
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


# retrieve actual host list for shortcut
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


# used for tab completion get a matching list of host for text input
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


# used for tab completion get a matching list of groups for text input
def groups_startswith(text):
    groups = host_groups.keys()
    return [host for host in groups if host.startswith(text)]

parse_hosts(ssh_config_file)


# Interactive Shell
class FechserShell(cmd.Cmd):
    prompt = TERM_BOLD + TERM_YELLOW + '(fechser)$ ' + TERM_RESET

    def __init__(self):
        super(FechserShell, self).__init__()

    # --------------commands--------------- #
    def do_hostname(self, arg):
        'Toggle if current hostname sould be displayed instead of the '\
            'Fechser title\ntype it again to switch back: hostname'
        global hostname
        if hostname is True:
            hostname = False
        else:
            hostname = True

    def do_connect(self, arg):
        'Connect to specified host: connect valkyr'
        global error_message
        host = get_host_for_shortcut(arg)
        if host is False:
            error_message = 'unknown/undefined shortcut'
        else:
            connect_host(host)
            time.sleep(1)

    def do_update(self, arg):
        'Update specified host: update painkiller \n' \
            'Update all hosts:      update all '
        global error_message
        if arg == 'all':
            # travers through dictionary entries
            for key_value_pair in host_groups.items():
                # access the values which are lists of hosts
                # and the value is a single host
                for host in key_value_pair[1]:
                    update_host(host)
                    print_hline()
                    time.sleep(1)
        else:
            host = get_host_for_shortcut(arg)
            if host is False:
                error_message = 'unknown/undefined shortcut'
            else:
                update_host(host)
                print_hline()
                time.sleep(3)

    def do_update_group(self, arg):
        'Update specified group: update_group work'
        global error_message
        try:
            hosts_list = host_groups[arg]
            for host in hosts_list:
                update_host(host)
                print_hline()
                time.sleep(1)
        except KeyError:
            error_message = 'unknown/undefined shortcut'

    def do_list(self, arg):
        'List all available shortcuts for managed hosts: list'
        build_screen()

    def do_exit(self, arg):
        'Exit/quit the Fechser shell: exit'
        global error_message
        error_message = 'Thank you for using Fechser to manage your digital offspring!'
        return True

    # --------------tab completion--------------- #
    def complete_connect(self, text, line, begidx, endidx):
        return hosts_startswith(text)

    def complete_update(self, text, line, begidx, endidx):
        result = hosts_startswith(text)
        if text == '' or 'all'.startswith(text):
            result.append('all')
        return result

    def complete_update_group(self, text, line, begidx, endidx):
        return groups_startswith(text)

    # ------------aux cmd functions------------- #
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
    FechserShell().cmdloop()
