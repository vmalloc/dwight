ROOT_IMAGE = "http://server/ubuntu_precise64.squashfs"

INCLUDES = {
    "/mounts/fetched_from_local_path" : Include("/local/path"),
}

ENVIRON = {
    "PATH" : "$PATH:some_path_here"
    }
