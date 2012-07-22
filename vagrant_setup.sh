!# /bin/sh

sudo apt-get install -y python-setuptools build-essential python-dev
sudo pip install nose
pushd ~vagrant/src
sudo python setup.py develop
popd
