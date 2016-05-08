# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"

  config.vm.network "private_network", ip: "192.168.36.36"

  config.vm.provider "virtualbox" do |vb|
     vb.memory = "2048"
     vb.cpus = 2
     vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
     vb.customize ["guestproperty", "set", :id, "/VirtualBox/GuestAdd/VBoxService/--timesync-set-threshold", 59000]
  end

  # This provisioner runs on the first `vagrant up`.
  config.vm.provision "install", type: "shell", inline: <<-SHELL
    # Add Docker apt repository
    sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
    sudo sh -c 'echo deb https://apt.dockerproject.org/repo ubuntu-trusty main > /etc/apt/sources.list.d/docker.list'
    sudo apt-get update -y
    # Uninstall old lxc-docker
    apt-get purge lxc-docker
    apt-cache policy docker-engine
    # Install docker and dependencies
    sudo apt-get install -y linux-image-extra-$(uname -r)
    sudo apt-get install -y docker-engine
    # Add user vagrant to docker group
    sudo groupadd docker
    sudo usermod -aG docker vagrant
    # Install Docker Compose
    curl -L https://github.com/docker/compose/releases/download/1.5.2/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    # Run docker-compose (which will update preloaded images, and
    # pulls any images not preloaded)
    cd /vagrant
  SHELL

  # This provisioner runs on every `vagrant reload' (as well as the `vagrant up`), reinstalling from local directories
  config.vm.provision "recompose", type: "shell",
     run: "always", inline: <<-SHELL

    # Run docker-compose (which will update preloaded images, pulls any images not preloaded)
    cd /vagrant

    # Get GID for DOCKER_UIDGID env var
    GID=`id -g`

    # Start services
    DOCKER_UIDGID="${UID}:${GID}" docker-compose up -d
  SHELL
end
