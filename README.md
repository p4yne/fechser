kroppzeug
=========

Helps you to manage your server kindergarten!


About
-----

Kroppzeug helps you to manage your server kindergarten by parsing your
SSH config file and providing shortcuts for connecting to a server or
updating one or all servers. Kroppzeug is perfect for managing a few to
a dozent servers but may be no fun when you have to orchestrate hundreds
or thousands of servers. It requires that you use a terminal multiplexer
like screen or tmux after connecting to a server.
Trivia: 'Kroppzeug' is an often lovingly and sometimes snidely used
low-german term for ones offspring.


Configuration
-------------

Just annotate your SSH config file with comments starting with '#kroppzeug_'.


* ``#kroppzeug_autocmd`` Commands to execute after the connection has been made. If value is ``false`` no command is executed.
* ``#kroppzeug_description`` A description of the server. Optional.
* ``#kroppzeug_update`` Commands to execute when using the update function. Optional.
* ``#kroppzeug_ssh`` Default is to use ssh, but setting this to e.g. ssh -vvv  will generate very very verbose ssh output or to mosh  which will be used then to connect to the server. Optional.
* ``#kroppzeug_managed`` Set to 'true' to allow kroppzeug to list this server.


Note: ``#kroppzeug_managed`` must be set to 'true' to enable a host entry. Furthermore, it must be the last of the comments for that host.
If ``#kroppzeug_ssh`` is changed to something else than 'ssh' like 'mosh' than the ``#kroppzeug_autocmd`` option must be set to 'false' because 'mosh' does not support the '-t' option to execute a command.

````
Host cloud
    Hostname                cloud.nonattached.net
    User                    user1
    Port                    2222
    #kroppzeug_autocmd      tmux attach || tmux
    #kroppzeug_description  OwnCloud Server
    #kroppzeug_update       apt-get update; apt-get upgrade
    #kroppzeug_managed      true
````

Additional Example snippets:

````
Host server
    Hostname                webserver.nonattached.net
    User                    user1
    Port                    2222
    #kroppzeug_autocmd      false
    #kroppzeug_description  OwnCloud Server
    #kroppzeug_update       sudo apt-get update; sudo apt-get upgrade
    #kroppzeug_managed      true
````

````
Host fun
    Hostname                lucky.nonattached.net
    User                    user1
    Port                    2222
    #kroppzeug_autocmd      false
    #kroppzeug_description  Happy Cats
    #kroppzeug_update       yaourt -Syua
    #kroppzeug_ssh          mosh
    #kroppzeug_managed      true
````

Commands
--------

To connect to a server just type the coresponding ``[server name]``.
To update a server use ``!update [server name]`` or ``!update-all`` to update
all servers. If you are unsure from which host you are connecting, e.g.
because you own too many computers, type ``!hostname`` to toggle the hostname
in the title area. You can always leave kroppzeug by typing ``!exit`` or using
CTRL+C or CTRL+D.


Screenshot
----------
````
                     ┬┌─┬─┐┌─┐┌─┐┌─┐┌─┐┌─┐┬ ┬┌─┐
                     ├┴┐├┬┘│ │├─┘├─┘┌─┘├┤ │ ││ ┬
                     ┴ ┴┴└─└─┘┴  ┴  └─┘└─┘└─┘└─┘
─────────────────────────────────────────────────────────────────────
     nan-gw Gateway Frankfurt         nan-vpn VPN Terminator IPMI
     puppet Puppet Master                  ns Nameserver (master)
       dns1 RDNSS 1                      dns2 RDNSS 2
       mail Mailserver                    www Webserver
     nethop Shell                         gws Gateway E.
    storage Storage E.                sealand Backup Server
        irc IRC Server                  cloud OwnCloud Server
        git GIT Repository                jmp VPN server
   workshop IPv6-Workshop

─────────────────────────────────────────────────────────────────────
(kroppzeug)$
````

License
-------

Copyright 2012-2014 Dan Luedtke <mail@danrl.de>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
