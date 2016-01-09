'use strict';

var constants = require('../testConstants.json');

var editAccountPage = function () {
	this.newFirstName = "Bill";
	this.newLastName = "Brown";
	this.newEmail = "billbrown@gmail.com";
	this.newUserDesignation = 3;
	
	this.title = element(by.binding('editCtrl.getTitle'))
	this.firstName = element(by.model('editCtrl.account.first_name'));
	this.lastName = element(by.model('editCtrl.account.last_name'));
	this.email = element(by.model('editCtrl.account.email'));
	this.emailError = element(by.binding('editCtrl.emailError'));
	this.userDesignation = element(by.model('editCtrl.account.user_designation'));
	this.userDesignationOptions = element.all(by.options("set.id as set.name for set in editCtrl.permissionsSets.results"));
	this.permissions = {};
	this.permissions.irf_view = element(by.binding('editCtrl.account.permission_irf_view'));
	this.permissions.irf_add = element(by.binding('editCtrl.account.permission_irf_add'));
	this.permissions.irf_edit = element(by.binding('editCtrl.account.permission_irf_edit'));
	this.permissions.irf_delete = element(by.binding('editCtrl.account.permission_irf_delete'));
	this.permissions.vif_view = element(by.binding('editCtrl.account.permission_vif_view'));
	this.permissions.vif_add = element(by.binding('editCtrl.account.permission_vif_add'));
	this.permissions.vif_edit = element(by.binding('editCtrl.account.permission_vif_edit'));
	this.permissions.vif_delete = element(by.binding('editCtrl.account.permission_vif_delete'));
	this.permissions.border_stations_view = element(by.binding('editCtrl.account.permission_border_stations_view'));
	this.permissions.border_stations_add = element(by.binding('editCtrl.account.permission_border_stations_add'));               
	this.permissions.border_stations_edit = element(by.binding('editCtrl.account.permission_border_stations_edit'));                
	this.permissions.border_stations_delete = element(by.binding('editCtrl.account.permission_border_stations_delete'));                
	this.permissions.accounts_manage = element(by.binding('editCtrl.account.permission_accounts_manage'));
	this.permissions.receive_email = element(by.binding('editCtrl.account.permission_receive_email'));
	this.permissions.vdc_manage = element(by.binding('editCtrl.account.permission_vdc_manage'));
	this.permissions.budget_manage = element(by.binding('editCtrl.account.permission_budget_manage'));
	this.updateButton = element(by.binding('editCtrl.getUpdateButtonText'));
	
	
	this.navigateToPage = function() {
		return browser.get(constants.webAddress + '/accounts/update/23');
	}
	
	this.update = function() {
		return this.updateButton.click();
	}.bind(this);
	
	this.changeUserInfo = function() {
		var self = this;
		return this.firstName.clear().sendKeys(self.newFirstName).then(function() {
		 	return self.lastName.clear().sendKeys(self.newLastName);
		}).then(function() {
			return self.email.clear().sendKeys(self.newEmail);			
		}).then(function() {
			return self.userDesignationOptions.get(3).click();			
		});
	}.bind(this);
	
	this.clearEmailField = function() {
		return this.email.clear();
	}.bind(this);
	
	this.clickAllPermissions = function(state) {
		var self = this;
		return this.permissions.irf_view.click().then(function () {
			return self.permissions.irf_add.click();
		}).then(function(){
			return self.permissions.irf_edit.click();
		}).then(function(){
			return self.permissions.irf_delete.click();			
		}).then(function(){
			return self.permissions.vif_view.click();			
		}).then(function(){
			return self.permissions.vif_add.click();				
		}).then(function(){
			return self.permissions.vif_edit.click();			
		}).then(function(){
			return self.permissions.vif_delete.click();			
		}).then(function(){
			return self.permissions.border_stations_view.click();			
		}).then(function(){
			return self.permissions.border_stations_add.click();
		}).then(function(){
			return self.permissions.border_stations_edit.click();
		}).then(function(){
			return self.permissions.border_stations_delete.click();
		}).then(function(){
			return self.permissions.accounts_manage.click();
		}).then(function(){
			return self.permissions.receive_email.click();
		}).then(function(){
			return self.permissions.vdc_manage.click();
		}).then(function(){
			return self.permissions.budget_manage.click();
		});		
	}.bind(this);

}

module.exports = new editAccountPage();