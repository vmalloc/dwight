# What is Dwight?

`dwight` is a utility for managing and deploying chrooted environments with external dependencies. `dwight` reads a configuration file that specifies how to establish the environment, and then allows you to run commands and interact with the environment.

Chrooted environments are constructed from a base image (currently only *squashfs* images are supported). External dependencies can then be added on to specified paths at construction time (these paths must exist in the base image as empty directories, as this is done via `mount`).

# Installation

`dwight` can be installed via `pip`:

      pip install dwight-chroot
  
# Usage

To run `dwight` you'll need a configuration file. A configuration file should at least contain the location of the base image. Here is a minimal configuration file:

      ROOT_IMAGE = "/path/to/image.squashfs"
 
Now just run:

      dwight -c /path/to/config_file.py shell
 
This will drop you into a shell in your chrooted environment.

# Configuration

Dwight receives its configuration from files specified with the *-c* flag. Multiple files can be specified for this option.

Dwight configuration files are simple Python files that contain settings in the form of underscore-separated uppercase strings (like THIS_ONE). variables not matching that criterion will be silently ignored (enabling you to use them for temporary variables etc.).

When Dwight loads configuration, it first looks for `~/.dwightrc` and loads it. If it doesn't exist an empty one will be created. Afterwards each configuration file from command line is loaded in turn, and the end result is the aggregation of all the config files.

**PLEASE NOTE** that when a configuration file is processed it has access to the parameters set by previous configuration files, so it can choose whether to override them or extend them. This is important, for instance, when using the `INCLUDES` option -- assigning to it will drop previous entries, so prefer using the `+=` operator instead.

## ROOT_IMAGE

The path to the root image for the chroot. This can also be a URL to an image file over http.

## INCLUDES

To bind paths or resources to your chroot environment, use the `INCLUDES` varaible in your configuration file:

      INCLUDES += [
        Include("/path/in/chroot", "/local/path"),
      ]

`INCLUDES` is a list of `Include` declarations. Each has a first argument which is the *destination* inside the chroot, and a second argument which is the resource to be `Include`ed.

Severl types of resources can be included, as describe below.

### Local Paths

Local paths get included as bind-mounts. If the path specified is a relative path, it is taken relative to the current working directory (useful for home dir mounting, for example)

### Git/Mercurial Repositories

Git and Mercurial repositories can be included. They are designated by using resource paths starting with `git://`, `ssh+git://`, `http+hg://` or `https+hg://`. They also take additional optional parameters, for example:

        Include("/path", "git://server/git/repository", branch="development") # cloning a specific branch
        Include("/path", "git://server/git/repository", tag="rc1") # clone a specific tag
        Include("/path", "git://server/git/repository", commit="4ff7a0565964eb428e5b45479922f164a5ee941b") # specific commit

### Squashfs Images

You can include whole images saved as **squashfs** files. This can be done from a local path:

        Include("/mount", "/path/to/image.squashfs")

Or from http/https:

        Include("/mount", "http://server/files/image.squashfs")

## ENVIRON

You can control the environment variables set up by dwight using the `ENVIRON` variable in your configuration file:

      ENVIRON = {
           "PATH" : "$PATH:another/extra/path/here"
      }

## PWD

The working directory for the command to run. By default this is the working directory in which `dwight` was run.

## UID/GID

You can control the uid/gid of the chrooted command. 

If the value is an integer, it will be used as the user id or the group id to execute commands.

If the value is None, Dwight will attempt to fetch the uid from the `SUDO_UID`/`SUDO_GID` environment variables. If the variable does not exist, the command will run as root.

## NUM_LOOP_DEVICES

This optional variable controls the amount of loop devices to ensure before `chroot`ing. If it is set, and no hard limit is configured for number of loop devices, `dwight` will ensure this number of loop devices exists in `/dev`.

## MAX_CACHE_SIZE

The maximum size, in bytes, that the cache directory can occupy. Note that the total size of the cache directory may still exceed this value some times, like in cases where all the space is needed for current includes.

# Known Issues

* Currently including a single git/hg repository multiple times with different commits/branches/tags will cause separate copies of the repository in the cache

# Extending, Modifying and Testing the Code

The tests included in dwight are intended to be run in a dedicated environment set up by [vagrant](http://vagrantup.com). To get started, install `vagrant`, and then run `vagrant up` from the project directory to start the environment.

To run the tests, ssh into the client vm and run via nosetests like so:

      $ vagrant ssh client
      vagrant@client:~$ sudo nosetests -w src/tests

# Acknowledgements

Special credit and thanks go to **Yotam Rubin**, who came up with the idea and drove this project forward.

# LICENSE

Dwight is distributed under the BSD 3-clause license. (See `LICENSE`)
