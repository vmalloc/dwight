# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.box = "precise64"

  config.vm.share_folder "src", "/home/vagrant/src", "."
  config.vm.share_folder "images", "/dwight-images", "/tmp/dwight-images"
  config.vm.provision :shell, :path => "vagrant_setup.sh"

end
