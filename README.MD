Item Catalog
------------
Item Catalog is an application that provides a list of items within a variety of
categories and integrate third party user registration and authentication.
Authenticated users should have the ability
to post, edit, and delete their own items.


Getting Started
----------------------
Install Vagrant and VirtualBox if you have not done so already.
Clone the git@github.com:Windesson/fullstack-nanodegree-vm.git repository.

Fetch the Source Code and VM Configuration
------------------------------------------
Windows: Use the Git Bash program (installed with Git) to get a Unix-style terminal.
Other systems: Use your favorite terminal program.

From the terminal, run:

git clone git@github.com:Windesson/Catalog.git catalog

This will give you a directory named catalog complete with the source code for the
flask application, a vagrantfile, and a pg_config.sh file for installing all of
the necessary tools.

1. run sudo ./pg_config.sh

2. run database_setup.py to create the database

3. run lotsofmenus.py to populate the database

4. run python ./webserver.py
