sudo apt-get install -y python-setuptools build-essential python-dev
sudo easy_install nose ipdb ipdbplugin ipython
pushd ~vagrant/src
sudo python setup.py develop
popd
