'use strict';

var constants = require('../testConstants.json');
var commonMethods = require('../commonMethods.js');

var permissionsPage = function() {
    var page = this;

    this.isElementStale = function(WebElement) {

        try {
            var temp = WebElement.tagName;
        }
        catch(StaleElementReferenceException) {
            return True
        }

        return false
    };

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
        browser.sleep(1000);
        this.accountPermission = element(by.partialLinkText("Access Control")).click();
        browser.sleep(1000);
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
        commonMethods.click(element(by.id(permission)).element(by.xpath('..')));
    };

    this.checkPermissionSetup = function(permission) {
        this.navigateToAccountPage();
        this.resetPermissions();
        this.checkPermission(permission);
    };

    this.checkPermissionCleanup = function() {
        this.navigateToAccountPage();
        this.resetPermissions();
        this.savePermissions();
    };

    this.savePermissions = function() {
        this.submit = element(by.className("btn-primary")).click();
    };

    this.viewVifForm = function() {
        browser.sleep(10000);
        this.view = element(by.linkText("View")).click();
    };

    this.resetPermissions = function() {
        element.all(by.className("btn-danger")).click();
    };

};

module.exports = new permissionsPage();