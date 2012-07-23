# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.define :client do |client_config|
      client_config.vm.box = "precise64"
      client_config.vm.box_url = "http://files.vagrantup.com/precise64.box"
      client_config.vm.host_name = "client"
      client_config.vm.share_folder "src", "/home/vagrant/src", "."
      client_config.vm.provision :shell, :path => "vagrant_setup_client.sh"
      client_config.vm.network :hostonly, "192.168.1.10"
  end

  config.vm.define :server do |server_config|
      server_config.vm.box = "precise64"
      server_config.vm.box_url = "http://files.vagrantup.com/precise64.box"
      server_config.vm.host_name = "server"
      server_config.vm.provision :shell, :path => "vagrant_setup_server.sh"
      server_config.vm.network :hostonly, "192.168.1.11"
  end

end
