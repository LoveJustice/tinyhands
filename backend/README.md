# Dream Suite
Tiny Hands International

[ ![Codeship Status for tu-software-studio/tinyhandsdreamsuite](https://www.codeship.io/projects/79c5fb20-1e83-0132-0c4f-7a12a542bc63/status?branch=master)](https://www.codeship.io/projects/35545)

# Installation

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
All you have to do is run the command `./manage.py test`.

## E2E Testing:
### setting up npm on our machines
 1.  `% mkdir "$HOME/npm"`
 2.  `% npm config set prefix "$HOME/npm"`
 3.  `% printf "NODE_PATH=$NODE_PATH:$HOME/npm/lib/node_modules\nPATH=$PATH:$HOME/npm:$HOME/npm/bin\n" >> ~/.bashrc && source ~/.bashrc`
 4.  `% npm install -g protractor`
 5.  `% npm install -g angular`
 6.  `% webdriver-manager update`
 7.  Install Chrome since that is what we are targeting for our tests.

### Running the tests
1. Execute the `./rune2etests.sh` test script which will run all the e2e tests specified in the `e2etesting/conf.js` file.
2. Watch the magic.

## Angular Testing with Karma
1. Make sure you have all of the dependencies downloaded by running `npm install`.
2. Start the Karma server with `./node_modules/karma/bin/karma start` if you are in the root project directory.
3. Watch the magic.
