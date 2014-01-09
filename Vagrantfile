
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu12_64"
  config.vm.box_url = "http://cloud-images.ubuntu.com/quantal/current/quantal-server-cloudimg-vagrant-amd64-disk1.box"

  config.vm.network :forwarded_port, guest: 80, host: 3080      # web, via nginx
  config.vm.network :forwarded_port, guest: 8000, host: 3070    # direct django
  config.vm.network :forwarded_port, guest: 22, host: 2275      # unique ssh
  
  # config.vm.synced_folder "../django/", "/home/vagrant/app/django"
  # config.vm.synced_folder "src/", "/home/vagrant/app/src"


  config.ssh.forward_agent = true
end