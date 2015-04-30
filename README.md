# Dream Suite
Tiny Hands International

[ ![Codeship Status for tu-software-studio/tinyhandsdreamsuite](https://www.codeship.io/projects/79c5fb20-1e83-0132-0c4f-7a12a542bc63/status?branch=master)](https://www.codeship.io/projects/35545)

# Testing:
### E2E Testing:
##### setting up npm on our machines
 1.  $ mkdir "$HOME/npm"
 2.  $ npm config set prefix "$HOME/npm"
 3.  add it to your path
    1.  $ printf "NODE_PATH=$NODE_PATH:$HOME/npm/lib/node_modules\nPATH=$PATH:$HOME/npm:$HOME/npm/bin\n" >> ~/.bashrc && source ~/.bashrc
 4.  npm install -g protractor
 5.  npm install -g angular
 6.  webdriver-manager update
 7.  Install Chrome since that is what we are targeting for our tests

##### Running the tests
1. Execute the ./rune2etests.sh test script which will run all the e2e tests specified in the e2etesting/conf.js file.
2. Watch the magic

### Django Testing:
All you have to do is run the command "./manage.py test"

### Angular Testing with Karma
1. make sure you have all of the dependencies downloaded by running "npm install"
2. Start the Karma server with "./node_modules/karma/bin/karma start" if you are in the root project directory
3. Watch the magic.

### Running Karma Tests
---
 * First install packages using `npm install`, or follow directions [here](http://karma-runner.github.io/0.12/intro/installation.html)
 * Then run `./node_modules/karma/bin/karma start` to start the karma server.

**NOTE**: Also check out [this](https://www.airpair.com/angularjs/posts/testing-angular-with-karma)
Resource to learn how to do [unit-tests](http://www.tuesdaydeveloper.com/2013/06/angularjs-testing-with-karma-and-jasmine/) in jasmine.
