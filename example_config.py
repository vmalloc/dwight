ROOT_IMAGE = "http://server/ubuntu_precise64.squashfs"

INCLUDES = [
    Include("/mounts/fetched_from_local_path", "/local/path"),
    Include("/mounts/fetched_from_git", "git://server/git/git_repository"),
    Include("/mounts/fetched_from_git_branch", "git://server/git/git_repository", branch="branch"),
    Include("/mounts/fetched_from_http", "http://server/fetched_from_http.squashfs"),
    Include("/mounts/fetched_from_hg", "http+hg://server:8000/repository"),
    Include("/mounts/fetched_from_hg_branch", "http+hg://server:8000/repository", branch="branch"),
]

ENVIRON = {
    "PATH" : "$PATH:some_path_here"
    }
