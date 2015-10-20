# Dream Suite
Tiny Hands International

[ ![Codeship Status for tu-software-studio/tinyhandsdreamsuite](https://www.codeship.io/projects/79c5fb20-1e83-0132-0c4f-7a12a542bc63/status?branch=master)](https://www.codeship.io/projects/35545)

# Vagrant setup #
1. make sure you have the latest version of [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/wiki/Downloads) installed 
2. if you are on windows, you should install [gitbash](https://git-scm.com/downloads) for easiness and niceness
3. clone the repository
4. cd into the project directory
5. execute `vagrant up`

### Vagrant Cheat Sheet ###
  `vagrant up` Turn on the virtual machine
  `vagrant halt` Turn off the virtual machine
  `vagrant reload` Restart the virtual machine
  `vagrant ssh` Open a bash session in the virtual machine

# Manual Installation #
As of 15-May-2015, these instructions were verified on a clean, fully-updated, Ubuntu 14.04 installation. Both Server and Desktop editions of Ubuntu work.

Install these modules (`sudo apt-get install <module name>`).

      git
      virtualenvwrapper
      python-dev
      libncurses5-dev
      libxml2-dev
      libxslt-dev
      zlib1g-dev
      libjpeg-dev

Clone the repository.

    % git clone ...

Make a virtual environment. You may need to close and re-open your shell after installing `virtualenvwrapper` in order to pick up the new commands defined by that package.

    % mkvirtualenv tinyhands
    % cd tinyhands
    % setvirtualenvproject

Install Python modules.

    % pip install -r requirements.txt

Set Django environment variable (put this in your `.bashrc` or in the virtual environment's `postactivate` file).

    % export DJANGO_SETTINGS_MODULE=dreamsuite.settings.local

Initialize the database.

    % ./manage.py migrate

Load the fixtures into the database.

    % ./bin/load-data.sh

Run the server.

    % ./manage.py runserver

# Testing
## Django Testing:
All you have to do is run the command `./manage.py test` in the project directory.

## E2E Testing:
### setup on our lab machines ###
 1.  `% mkdir "$HOME/npm"`
 2.  `% npm config set prefix "$HOME/npm"`
 3.  `% printf "NODE_PATH=$NODE_PATH:$HOME/npm/lib/node_modules\nPATH=$PATH:$HOME/npm:$HOME/npm/bin\n" >> ~/.bashrc && source ~/.bashrc`
 4.  `% npm install -g protractor`
 5.  `% npm install -g angular`
 6.  `% webdriver-manager update`
 7.  Install Chrome since that is what we are targeting for our tests.

### Windows using vagrant ###
 1. Download and install the latest version of node `https://nodejs.org/en/` on your Windows machine
 2. then use gitbash to install protractor `npm install -g protractor`
 3. update webdriver-manager `webdriver-manager update`
 
### Running the tests on unix ###
1. Execute the `./bin/rune2etests.sh` test script which will run all the e2e tests specified in the `e2etesting/conf.js` file.
2. Watch the magic.

### Running the tests on a Vagrant setup ###
1. first ssh into the vagrant box with the `vagrant ssh` command
2. Then cd into the synced folder `cd tinyhands`
3. Execute the `./bin/windows-run-e2e-tests.sh` script which will setup the database and run the test server.
4. open another gitbash terminal and start the webdriver server with `webdriver-manager start` 
5. finally open another gitbash terminal to the project directory and execute `protractor e2etesting/conf.js` to run the tests
6. watch the magic happen

## Angular Testing with Karma ##
1. Make sure you have all of the dependencies downloaded by running `npm install`. 
2. Install karma cli `npm install -g karma-cli`. (if on windows remember to install on your host machine)
3. Start the Karma server with `karma start` if you are in the root project directory.
4. Watch the magic.

#Installing sanitized prodution database
1. cd to the top level tinyhands directory
2. Make sure there is not already a db.sqlite3 in the top level tinyhands directory
3. Execute etc/bin/install_test_db.sh
    The sanitized database has two accounts preconfigured for testing both of which have the password 'pass'
    1) test_sup@example.com - is a super user account
    2) test1 - is a user account
