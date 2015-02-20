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

    this.navigateToAccountPage = function(){
        browser.get('http://0.0.0.0:8000/accounts/update/22/');
    };

    this.navigateToIrfPage = function() {
        browser.get('http://0.0.0.0:8000/data-entry/irfs/search/');
    };

    this.checkPermission = function(permission) {
        this.permissions = element(by.id(permission));
        console.log(this.permissions);
        this.button = this.permissions.element(by.xpath('..'));
        this.button.click();
    };

    this.savePermissions = function() {
        this.submit = element(by.className("btn-primary")).click();

    };

    this.resetPermissions = function() {
        element.all(by.className("btn-danger")).click();
    };

    this.uncheckAllPermissions = function() {
        this.checkPermission("id_permission_irf_view");
        this.checkPermission("id_permission_irf_add");
        this.checkPermission("id_permission_irf_edit");
        this.checkPermission("id_permission_vif_view");
        this.checkPermission("id_permission_vif_add");
        this.checkPermission("id_permission_vif_edit");
        this.checkPermission("id_permission_border_stations_view");
        this.checkPermission("id_permission_border_stations_add");
        this.checkPermission("id_permission_border_stations_edit");
    };

};

module.exports = new permissionsPage();