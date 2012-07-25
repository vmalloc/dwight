echo "192.168.1.10 client" >> /etc/hosts
sudo apt-get install -y python-setuptools build-essential python-dev debootstrap squashfs-tools libnss-mdns

# setup git server
sudo apt-get -y install git-daemon-run

cat <<"EOF" > /etc/sv/git-daemon/run
#!/bin/sh
exec 2>&1
echo 'git-daemon starting.'
exec chpst -ugitdaemon \
  "$(git --exec-path)"/git-daemon --verbose --reuseaddr \
    --export-all --base-path=/var/cache /var/cache/git
EOF
sudo sv restart git-daemon

# setup web server
sudo apt-get -y install nginx
sudo service nginx start

# setup base mount (published via web)
mkdir -p /tmp/base_image
sudo debootstrap --variant=buildd --arch amd64 precise /tmp/base_image http://archive.ubuntu.com/ubuntu/
sudo touch /tmp/base_image/dwight_base_image_file
sudo mkdir -p /tmp/base_image/mounts/{fetched_from_git,fetched_from_http,fetched_from_ssh,fetched_from_local_path}
mksquashfs /tmp/base_image /usr/share/nginx/www/ubuntu_precise64.squashfs

# setup external squashfs (to be exported over http)
mkdir /tmp/external_image
touch /tmp/external_image/fetched_from_http_file
mksquashfs /tmp/external_image /usr/share/nginx/www/fetched_from_http.squashfs

# setup git repository
pushd /var/cache/git
git init git_repository
pushd git_repository
touch fetched_from_git_file
git add .
git commit -a -m init
