'use strict';

var constants = require('../testConstants.json');

var accessDefaultsPage = function() {
    var page = this;

    this.navigateToAccessControl = function() {
        return browser.get(constants.webAddress + '/accounts/access-defaults/');
    };

    this.addPermissionSetRow = function() {
        var addAnotherButton = element(by.id('add-another'));
        return addAnotherButton.click();
    };

    this.getPermissionSetRow = function(rowNumber) {
        var idPrefix = 'id_form-' + rowNumber + '-permission_';
        
        var row = {};
        row.designation = element(by.id('id_form-' + rowNumber + '-name'));
        row.irfView = element(by.id(idPrefix + 'irf_view'));
        row.irfAdd = element(by.id(idPrefix + 'irf_add'));
        row.irfEdit = element(by.id(idPrefix + 'irf_edit'));
        row.irfDelete = element(by.id(idPrefix + 'irf_delete'));
        row.vifView = element(by.id(idPrefix + 'vif_view'));
        row.vifAdd = element(by.id(idPrefix + 'vif_add'));
        row.vifEdit = element(by.id(idPrefix + 'vif_edit'));
        row.vifDelete = element(by.id(idPrefix + 'vif_delete'));
        row.borderStationView = element(by.id(idPrefix + 'border_stations_view'));
        row.borderStationAdd = element(by.id(idPrefix + 'border_stations_add'));
        row.borderStationEdit = element(by.id(idPrefix + 'border_stations_edit'));
        row.accountsManage = element(by.id(idPrefix + 'accounts_manage'));
        row.vdcManage = element(by.id(idPrefix + 'vdc_manage'));
        row.budgetManage = element(by.id(idPrefix + 'budget_manage'));        
        return row;
    };
}

module.exports = new accessDefaultsPage();
