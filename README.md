fechser
=========

Helps you to manage your server kindergarten!


About
-----

Kroppzeug helps you to manage your server kindergarten by parsing your
SSH config file and providing shortcuts for connecting to a server or
updating one or all servers. Fechser is perfect for managing a few to
a dozent servers but may be no fun when you have to orchestrate hundreds
or thousands of servers. It requires that you use a terminal multiplexer
like screen or tmux after connecting to a server.
Trivia: 'Fechser' is a lovingly baverian german term for ones offspring.


Configuration
-------------

Just annotate your SSH config file with comments starting with '#kf_'.


* ``#kf_autocmd`` Commands to execute after the connection has been made. If value is ``false`` no command is executed.
* ``#kf_description`` A description of the server. Optional.
* ``#kf_update`` Commands to execute when using the update function. Optional.
* ``#kf_ssh`` Default is to use ssh, but setting this to e.g. ssh -vvv  will generate very very verbose ssh output or to mosh  which will be used then to connect to the server. Optional.
* ``#kf_managed`` Set to 'true' to allow fechser to list this server.


Note: ``#kf_managed`` must be set to 'true' to enable a host entry. Furthermore, it must be the last of the comments for that host.
If ``#kf_ssh`` is changed to something else than 'ssh' like 'mosh' than the ``#kf_autocmd`` option must be set to 'false' because 'mosh' does not support the '-t' option to execute a command.

````
Host cloud
    Hostname                cloud.nonattached.net
    User                    user1
    Port                    2222
    #kf_autocmd      tmux attach || tmux
    #kf_description  OwnCloud Server
    #kf_update       apt-get update; apt-get upgrade
    #kf_managed      true
````

Additional Example snippets:

````
Host server
    Hostname                webserver.nonattached.net
    User                    user1
    Port                    2222
    #kf_autocmd      false
    #kf_description  OwnCloud Server
    #kf_update       sudo apt-get update; sudo apt-get upgrade
    #kf_managed      true
````

````
Host fun
    Hostname                lucky.nonattached.net
    User                    user1
    Port                    2222
    #kf_autocmd      false
    #kf_description  Happy Cats
    #kf_update       yaourt -Syua
    #kf_ssh          mosh
    #kf_managed      true
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
                     ┌─┐┌─┐┌─┐┬ ┬┌─┐┌─┐┬─┐
                     ├┤ ├┤ │  ├─┤└─┐├┤ ├┬┘
                     └  └─┘└─┘┴ ┴└─┘└─┘┴└─
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
(fechser)$
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
