echo "192.168.1.11 server" >> /etc/hosts

# setup packages
sudo apt-get install -y python-setuptools build-essential python-dev squashfs-tools libnss-mdns git
sudo easy_install nose ipdb ipdbplugin ipython
pushd ~vagrant/src
sudo python setup.py develop
popd
