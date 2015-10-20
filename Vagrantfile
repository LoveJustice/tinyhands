# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure(2) do |config|
    config.vm.box = "ubuntu/trusty64" # Set the box to run a 64bit trusty distribution
  
    # Forward port 8000 on vm to port 8080 on our host machine
    config.vm.network "forwarded_port", guest: 8000, host: 8000 # for the normal server
    config.vm.network "forwarded_port", guest: 8001, host: 8001 # for the e2e test server

    # Sync the folder the Vagrant file is in and set it to /home/vagrant/tinyhands
    config.vm.synced_folder "./", "/home/vagrant/tinyhands"

    # Modify the hardware specs of the VM
    config.vm.provider "virtualbox" do |vb|
      vb.memory = 1024
      vb.cpus = 1
    end

    # Found that this sped things up
    config.vm.provider "virtualbox" do |vb|
        vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    end

    # This provisioner runs on the first `vagrant up`.
    config.vm.provision "install", type: "shell", inline: <<-SHELL
        # Install required packages for TinyHands App
        apt-get update
        apt-get -y install git virtualenvwrapper python-dev libncurses5-dev libxml2-dev libxslt-dev zlib1g-dev dos2unix libjpeg-dev
        
        # Install Pip Packages
        cd /home/vagrant/tinyhands/
        pip install -r requirements.txt

        # Setup Database
        python manage.py migrate --noinput
        sh ./bin/load-data.sh
    SHELL

    # This provisioner runs on every `vagrant reload' (as well as the first `vagrant up`)
    config.vm.provision "recompose", type: "shell", run: "always", inline: <<-SHELL
        apt-get update
        apt-get -y upgrade

        cd /home/vagrant/tinyhands/

        export DJANGO_SETTINGS_MODULE=dreamsuite.settings.local 
        echo "export DJANGO_SETTINGS_MODULE=dreamsuite.settings.local" >> /home/vagrant/.bashrc
        echo 'alias run-server="./manage.py runserver 0.0.0.0:8000"' >> /home/vagrant/.bashrc
        echo 'alias run-test-server="./manage.py runserver 0.0.0.0:8000"' >> /home/vagrant/.bashrc

        # Install Pip Packages
        pip install -r requirements.txt
    SHELL
end