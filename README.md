# Dream Suite

Tiny Hands International

[ ![Codeship Status for tu-software-studio/tinyhandsdreamsuite](https://www.codeship.io/projects/79c5fb20-1e83-0132-0c4f-7a12a542bc63/status?branch=master)](https://www.codeship.io/projects/35545)

# Setup

## Docker

1. Make sure you have the latest version of [Docker](https://www.docker.com/) (The lab machines should be up to date, if not, talk to the Nates)
2. Install virutalenvwrapper `sudo apt-get install virtualenvwrapper`, create a new virtual environment `mkvirtualenv <name> -p /usr/bin/python2`, and enter it `workon <name>`
3. Install docker-compose, a tool that makes docker easier to use: `pip install docker-compose`
4. Clone the repository and cd into it
5. set the repo as the virtualenvs root `setvirtualenvproject`
6. Create the local.env file for docker-compose to use: `cp local.env.dist local.env`
7. Execute `docker-compose up -d` to build and run the project (This might take a few minutes the first time it is run)
8. Install the test database by cd-ing into application and executing `./etc/bin/install_test_db.sh`
9. Collect static files by running `docker-compose run --rm web ./manage.py collectstatic -l` (the -l command creates the static files as symlinks so you do not have to collect static every time you update the file, just for new files)
10. If all of the steps were successful, you can find the application running on [port 80 on localhost](http://localhost). If not, contact Ben Duggan through slack.

## Vagrant + Docker setup (For Windows or Mac)

1. make sure you have the latest version of [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/wiki/Downloads) installed
2. if you are on windows, you should install [gitbash](https://git-scm.com/downloads) for easiness and niceness
3. clone the repository
4. cd into the project directory
5. execute `vagrant up --provision`
6. the server will be listening on `192.168.36.36/` and then you `vagrant ssh` to get access to docker/docker-compose commands

## Installing Sanitized Test Data

1. cd into the application directory
2. make sure the application is running or start it (`docker-compose up -d`)
3. execute `./etc/bin/install_test_db.sh` and wait awhile.
- The sanitized database has two accounts preconfigured for testing both of which have the password 'pass'

  - test_sup@example.com - is a super user account
  - test1 - is a user account

## Docker/Docker-Compose Cheat Sheet

- `docker-compose up -d` Turn on all of the containers listed in the docker-compose.yml file
- `docker-compose kill <container name>*` Turn off the running containers
- `docker-compose rm <container name>*` Delete the containers
- `docker-compose run <container-name> <command>` Run a command inside of a copy of a container (or run bash so you can do multiple things)
- `docker-compose build` - rebuild the containers specified in the docker-compose.yml file
- `docker build -t tusoftware-studio/<container-name> <directory with a Dockerfile>` Build a container from a directory containing a Dockerfile
- `docker pull tusoftware-studio/<container-name>`
- `docker push tusoftware-studio/<container-name>`
- `docker stop $(docker ps -a -q)` - stop all running containers on machine
- `docker rm $(docker ps -a -q)` - remove all containers on machine
- `docker exec -it <container-id> bash` - run an interactive shell inside the actual container

# local.env and common.env files

In the root project directory there are three files that contain environment variable. These files are used inside of the containers. If you look at the docker-compose.yml file you can see that these are imported into all of the containers.

- common.env file: This is for key-value pairs that are okay to be public, but are good to be customizable for different development environments
- local.env file: This is for key-value pairs that should not be in version control. Think passwords, secret keys, other stuff you don't want the world knowing about (Since one day it would be nice to make this an open-source project)
- local.env.dist: This is where you put the keys that should go into the local.env file. In this file the format should be `<key>=`. This way we know what environment variables need to exist/be set, but we are not putting the actual secrets in version control

# Testing

## Django Unit Tests:

There is a test container that I created called test-django detailed in the docker-compose file

Simply execute the `./manage.py test` command in the test container. eg. `docker-compose run test-django ./manage.py test`

## E2E/Karma Tests:

```
In Development
```
