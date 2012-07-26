echo "192.168.1.10 client" >> /etc/hosts
sudo apt-get install -y python-setuptools build-essential python-dev debootstrap squashfs-tools libnss-mdns tmux

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

# setup mercurial server
sudo apt-get -y install mercurial

echo <<EOF > $HOME/.hgrc
[ui]
username = John Doe <john@example.com>
EOF

hg init $HOME/hgrepo
pushd $HOME/hgrepo
touch fetched_from_hg_file
hg add fetched_from_hg_file
hg commit -m "default commit"
# hg branch
hg branch branch
hg rm fetched_from_hg_file
touch fetched_from_hg_tag_file
hg add .
hg commit -m "tag commit"
hg tag tag
hg rm fetched_from_hg_tag_file
touch fetched_from_hg_branch_file
hg add .
hg commit -m "branch commit"
hg serve -d --prefix repository
popd

# setup web server
sudo apt-get -y install nginx
sudo service nginx start

# setup base mount (published via web)
mkdir -p /tmp/base_image
sudo debootstrap --variant=buildd --arch amd64 precise /tmp/base_image http://archive.ubuntu.com/ubuntu/
sudo touch /tmp/base_image/dwight_base_image_file

mkdir -p /tmp/base_image/mounts/
pushd /tmp/base_image/mounts/
sudo mkdir -p fetched_from_git fetched_from_hg fetched_from_http fetched_from_ssh fetched_from_local_path fetched_from_git_branch fetched_from_hg_branch
popd

mksquashfs /tmp/base_image /usr/share/nginx/www/ubuntu_precise64.squashfs

# setup external squashfs (to be exported over http)
mkdir /tmp/external_image
touch /tmp/external_image/fetched_from_http_file
mksquashfs /tmp/external_image /usr/share/nginx/www/fetched_from_http.squashfs

# setup git repository
git config --global user.name "John Doe"
git config --global user.email "johndoe@email.com"
pushd /var/cache/git
git init git_repository
pushd git_repository
git commit -a --allow-empty -m init
git checkout -b branch
touch fetched_from_git_tag_file
git add .
git commit -a -m "tag commit"
git rm fetched_from_git_tag_file
touch fetched_from_git_branch_file
git add .
git commit -a -m "branch commit"
git checkout master
touch fetched_from_git_file
git add .
git commit -a -m "master commit"
