ROOT_IMAGE = "/dwight-images/precise64.squashfs"

#EXTRAS = [
#   Include(source="git://....../...", dest="/blap/bloop", commit="..."),
#   Include(source="blapblapblap.squashfs", dest="/bloop/bloop"),
#   ]


ENVIRON = {
    'PATH' : '$PATH:build/python/verycoolpythonlib/bin:/opt/toolchain/bin',
    'PYTHONPATH' : '$PYTHONPATH:build/python/verycoolpythonlib'
    }

BIND_MOUNTS = {
    "/home": "/home/vagrant"
}
