echo "192.168.1.11 server" >> /etc/hosts

# setup packages
sudo apt-get install -y python-setuptools build-essential python-dev squashfs-tools libnss-mdns git mercurial
sudo easy_install nose ipdb ipdbplugin ipython
pushd ~vagrant/src
sudo python setup.py develop
popd

sudo mkdir -p /local/path
sudo touch /local/path/fetched_from_local_path_file
