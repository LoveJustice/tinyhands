'use strict';

var constants = require('../testConstants.json');

var permissionsPage = function() {
    var page = this;

    this.navigateToVdcPage = function() {
        browser.get(constants.webAddress + "/data-entry/geocodelocations/vdc-admin/");
    };

    this.navigateToBorderstationPage = function() {
        browser.get(constants.webAddress + "/static_border_stations/border-stations/0/")
    };

    this.navigateToAccounts = function(){
        browser.get(constants.webAddress + '/accounts');
    };

    this.navigateToAccessControl = function() {
        browser.get(constants.webAddress + '/accounts');
        this.accountPermission = element(by.partialLinkText("Access Control")).click();
    };

    this.navigateToVifPage = function() {
        browser.get(constants.webAddress + '/data-entry/vifs/search/');
    };

    this.navigateToAccountPage = function(){
        browser.get(constants.webAddress + '/accounts/update/22/');
    };

    this.navigateToIrfPage = function() {
        browser.get(constants.webAddress + '/data-entry/irfs/search/');
    };

    this.checkPermission = function(permission) {
        this.permissions = element(by.id(permission));
        this.button = this.permissions.element(by.xpath('..'));
        this.button.click();
    };

    this.savePermissions = function() {
        this.submit = element(by.className("btn-primary")).click();
    };

    this.viewVifForm = function() {
        this.view = element(by.linkText("View")).click();
    };

    this.resetPermissions = function() {
        element.all(by.className("btn-danger")).click();
    };

};

module.exports = new permissionsPage();