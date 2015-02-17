'use strict';

var constants = require('../testConstants.json');

var permissionsPage = function() {
    var page = this;

    this.navigateToAccounts = function(){
        browser.get('http://0.0.0.0:8000/accounts');
    };

    this.navigateToAccessControl = function() {
        browser.get('http://0.0.0.0:8000/accounts');
        this.accountPermission = element(by.partialLinkText("Access Control")).click();
    };

    this.navigateToVifPage = function() {
        browser.get('http://0.0.0.0:8000/data-entry/vifs/search/');
    };

    this.uncheckPermission = function(permission) {
        browser.get('http://0.0.0.0:8000/accounts/update/22/');
        this.permissions = element(by.id(permission)).checked = false;
    };

    this.checkAllPermissions = function() {
        browser.get('http://0.0.0.0:8000/accounts/update/22/');
    };

};

module.exports = new permissionsPage();