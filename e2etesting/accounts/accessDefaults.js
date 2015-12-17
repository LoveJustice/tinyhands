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
        row.permissions = {};
        row.permissions.irfView = permissionsSet.element(by.binding('permissionsSet.permission_irf_view ? "Yes" : "No"'));
        row.permissions.irfAdd = permissionsSet.element(by.binding('permissionsSet.permission_irf_add ? "Yes" : "No"'));
        row.permissions.irfEdit = permissionsSet.element(by.binding('permissionsSet.permission_irf_edit ? "Yes" : "No"'));
        row.permissions.irfDelete = permissionsSet.element(by.binding('permissionsSet.permission_irf_delete ? "Yes" : "No"'));
        row.permissions.vifView = permissionsSet.element(by.binding('permissionsSet.permission_vif_view ? "Yes" : "No"'));
        row.permissions.vifAdd = permissionsSet.element(by.binding('permissionsSet.permission_vif_add ? "Yes" : "No"'));
        row.permissions.vifEdit = permissionsSet.element(by.binding('permissionsSet.permission_vif_edit ? "Yes" : "No"'));
        row.permissions.vifDelete = permissionsSet.element(by.binding('permissionsSet.permission_vif_delete ? "Yes" : "No"'));
        row.permissions.borderStationView = permissionsSet.element(by.binding('permissionsSet.permission_border_stations_view ? "Yes" : "No"'));
        row.permissions.borderStationAdd = permissionsSet.element(by.binding('permissionsSet.permission_border_stations_add ? "Yes" : "No"'));
        row.permissions.borderStationEdit = permissionsSet.element(by.binding('permissionsSet.permission_border_stations_edit ? "Yes" : "No"'));
        row.permissions.borderStationDelete = permissionsSet.element(by.binding('permissionsSet.permission_border_stations_delete ? "Yes" : "No"'));
        row.permissions.alertsCanReceive = permissionsSet.element(by.binding('permissionsSet.permission_receive_email ? "Yes" : "No"'));
        row.permissions.accountsManage = permissionsSet.element(by.binding('permissionsSet.permission_accounts_manage ? "Yes" : "No"'));
        row.permissions.vdcManage = permissionsSet.element(by.binding('permissionsSet.permission_vdc_manage ? "Yes" : "No"'));
        row.permissions.budgetManage = permissionsSet.element(by.binding('permissionsSet.permission_budget_manage ? "Yes" : "No"'));
        return row;
    }
    
    this.clickRowPermissionButtons = function(row) {
        var permissions = row.permissions;
        for (var permissionButton in permissions) {
            if (permissions.hasOwnProperty(permissionButton)) {
                permissions[permissionButton].click();
            }
        }
    }; 
    
    this.saveAll = function() {
        var saveAllButton = element(by.buttonText('Save All'));
        return saveAllButton.click();
    }
}

module.exports = new accessDefaultsPage();
