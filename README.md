# What is Dwight?

`dwight` is a utility for managing and deploying chrooted environments with external dependencies. `dwight` reads a configuration file that specifies how to establish the environment, and then allows you to run commands and interact with the environment.

Chrooted environments are constructed from a base image (currently only *squashfs* images are supported). External dependencies can then be added on to specified paths at construction time (these paths must exist in the base image as empty directories, as this is done via `mount`).

# Installation

`dwight` can be installed via `pip`:

      pip install dwight-chroot
  
# Usage

## Basic Usage

To run `dwight` you'll need a configuration file. A configuration file should at least contain the location of the base image. Here is a minimal configuration file:

      ROOT_IMAGE = "/path/to/image.squashfs"
 
Now just run:

      dwight -c /path/to/config_file.py shell
 
This will drop you into a shell in your chrooted environment.

## Includes

To bind paths or resources to your chroot environment, use the `INCLUDES` varaible in your configuration file:

      INCLUDES = {
        "/path/in/chroot" : Include("/local/path"),
      }
 
The above example will bind-mount `/local/path` on your machine to the path `/path/in/chroot` (inside the chrooted environment).

## External Resources

Not only local directories can be `Include`ed. The following resources are supported:

* git repositories (resources starting with `git://` or `ssh+git://`)
* squashfs images on local machine (e.g. `/tmp/image.squashfs`)
* squashfs images on over http (e.g. `http://server/blap.squashfs`)

## Environment Variables

You can control the environment variables set up by dwight using the `ENVIRON` variable in your configuration file:

      ENVIRON = {
           "PATH" : "$PATH:another/extra/path/here"
      }


# Known Issues

* Currently including a single git/hg repository multiple times with different commits/branches will cause separate copies of the repository in the cache

# Extending, Modifying and Testing the Code

The tests included in dwight are intended to be run in a dedicated environment set up by [vagrant](http://vagrantup.com). To get started, install `vagrant`, and then run `vagrant up` from the project directory to start the environment.

To run the tests, ssh into the client vm and run via nosetests like so:

      $ vagrant ssh client
      vagrant@client:~$ sudo nosetests -w src/tests

# LICENSE

Dwight is distributed under the BSD 3-clause license. (See `LICENSE`)
