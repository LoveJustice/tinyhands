'use strict';

var constants = require('../testConstants.json');

var accessDefaultsPage = function() {
    var page = this;
    var permissionsSets = element.all(by.repeater("permissionsSet in defaultsCtrl.permissionsSets"));

    this.navigateToAccessDefaults = function() {
        return browser.get(constants.webAddress + '/accounts/access-defaults/');
    };

    this.addPermissionsSetRow = function() {
        var addAnotherButton = element(by.buttonText('Add Another'));
        return addAnotherButton.click();
    };

    this.getPermissionsSetRow = function(index) {
        var permissionsSet = permissionsSet[index];
        return populateRow(permissionsSet);
    };
    
    this.getSuperAdministratorRow = function() {
        return permissionsSets.filter(function(elem, index) {
            return elem.element(by.model('permissionsSet.name')).getAttribute('value').then(function(text) {
                return text === 'Super Administrator';
            });
        }).then(function(filteredElements) {
            return populateRow(filteredElements[0]);
        });
    }
    
    this.getLastPermissionsSetRow = function() {
        return populateRow(permissionsSets.last());
    }
    
    function populateRow(permissionsSet) {
        var row = {};
        row.deleteButton = permissionsSet.element(by.buttonText('X'));
        row.designation = permissionsSet.element(by.model('permissionsSet.name'));
        row.irfView = permissionsSet.element(by.binding('permissionsSet.permission_irf_view ? "Yes" : "No"'));
        row.irfAdd = permissionsSet.element(by.binding('permissionsSet.permission_irf_add ? "Yes" : "No"'));
        row.irfEdit = permissionsSet.element(by.binding('permissionsSet.permission_irf_edit ? "Yes" : "No"'));
        row.irfDelete = permissionsSet.element(by.binding('permissionsSet.permission_irf_delete ? "Yes" : "No"'));
        row.vifView = permissionsSet.element(by.binding('permissionsSet.permission_vif_view ? "Yes" : "No"'));
        row.vifAdd = permissionsSet.element(by.binding('permissionsSet.permission_vif_add ? "Yes" : "No"'));
        row.vifEdit = permissionsSet.element(by.binding('permissionsSet.permission_vif_edit ? "Yes" : "No"'));
        row.vifDelete = permissionsSet.element(by.binding('permissionsSet.permission_vif_delete ? "Yes" : "No"'));
        row.borderStationView = permissionsSet.element(by.binding('permissionsSet.permission_border_stations_view ? "Yes" : "No"'));
        row.borderStationAdd = permissionsSet.element(by.binding('permissionsSet.permission_border_stations_add ? "Yes" : "No"'));
        row.borderStationEdit = permissionsSet.element(by.binding('permissionsSet.permission_border_stations_edit ? "Yes" : "No"'));
        row.borderStationDelete = permissionsSet.element(by.binding('permissionsSet.permission_border_stations_delete ? "Yes" : "No"'));
        row.alertsCanReceive = permissionsSet.element(by.binding('permissionsSet.permission_receive_email ? "Yes" : "No"'));
        row.accountsManage = permissionsSet.element(by.binding('permissionsSet.permission_accounts_manage ? "Yes" : "No"'));
        row.vdcManage = permissionsSet.element(by.binding('permissionsSet.permission_vdc_manage ? "Yes" : "No"'));
        row.budgetManage = permissionsSet.element(by.binding('permissionsSet.permission_budget_manage ? "Yes" : "No"'));
        return row;
    }
    
    this.clickRowPermissionButtons = function(row) {
        row.irfView.click();
        row.irfAdd.click();
        row.irfEdit.click();
        row.irfDelete.click();
        row.vifView.click();
        row.vifAdd.click();
        row.vifEdit.click();
        row.vifDelete.click();
        row.borderStationView.click();
        row.borderStationAdd.click();
        row.borderStationEdit.click();
        row.borderStationDelete.click();
        row.alertsCanReceive.click();
        row.accountsManage.click();
        row.vdcManage.click();
        row.budgetManage.click();
    }; 
    
    this.saveAll = function() {
        var saveAllButton = element(by.buttonText('Save All'));
        return saveAllButton.click();
    }
}

module.exports = new accessDefaultsPage();
