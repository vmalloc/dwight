ROOT_IMAGE = "http://server/ubuntu_precise64.squashfs"

INCLUDES = {
    "/mounts/fetched_from_local_path" : Include("/local/path"),
    "/mounts/fetched_from_git" : Include("git://server/git/git_repository"),
}

ENVIRON = {
    "PATH" : "$PATH:some_path_here"
    }
