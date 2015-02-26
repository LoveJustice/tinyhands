'use strict';

var constants = require('../testConstants.json');

var loginPage = function () {
    var page = this;

    this.logout = function () {
        browser.get('http://0.0.0.0:8001/logout/');
    };

    this.login = function (username, password) {
        browser.get('http://0.0.0.0:8001/login/');
        this.usernamefield = element(by.id("id_username")).sendKeys(username);

        this.passwordfield = element(by.id("id_password")).sendKeys(password);
        this.submitButton = element(by.id("submit")).click();
    };

    this.loginAsAdmin = function () {
        this.login(constants.adminEmail, constants.adminPassword);
    };
};

module.exports = new loginPage();
