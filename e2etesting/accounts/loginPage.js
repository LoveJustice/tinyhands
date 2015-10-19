'use strict';

var constants = require('../testConstants.json');
var methods = require('../commonMethods.js');

var loginPage = function () {
    var page = this;

    this.logout = function () {
        browser.get('http://0.0.0.0:8001/logout/');
    };

    this.login = function (username, password) {
        browser.get('http://0.0.0.0:8001/login/');
        this.usernamefield = element(by.id("id_username")).clear().sendKeys(username);
        this.passwordfield = element(by.id("id_password")).clear().sendKeys(password);
        methods.click(element(by.id("submit")));
    };

    this.loginAsAdmin = function() {
		this.login(constants.adminEmail, constants.adminPassword);
    };
};

module.exports = new loginPage();
'use strict';

var c = require('../testConstants.json');
var methods = require('../commonMethods.js');

var loginPage = function () {
    var page = this;

    this.logout = function () {
        browser.get(c.webAddress + '/logout/');
    };

    this.login = function (username, password) {
        browser.get(c.webAddress + '/login/');
        this.usernamefield = element(by.id("id_username")).clear().sendKeys(username);
        this.passwordfield = element(by.id("id_password")).clear().sendKeys(password);
        methods.click(element(by.id("submit")));
    };

    this.loginAsAdmin = function() {
        this.login(c.adminEmail, c.adminPassword);
    };
};

module.exports = new loginPage();