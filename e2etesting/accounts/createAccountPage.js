'use strict';

var constants = require('../testConstants.json');

var createAccountPage = function () {
	this.newFirstName = "Bob";
	this.newLastName = "Brown";
	this.newEmail = "bobbrown@gmail.com";
	this.newUserDesignation = 3;
	
	this.title = element(by.binding('editCtrl.getTitle'))
	this.firstName = element(by.model('editCtrl.account.first_name'));
	this.lastName = element(by.model('editCtrl.account.last_name'));
	this.email = element(by.model('editCtrl.account.email'));
	this.emailError = element(by.binding('editCtrl.emailError'));
	this.userDesignation = element(by.model('editCtrl.account.user_designation'));
	this.userDesignationOptions = element.all(by.options("set.id as set.name for set in editCtrl.permissionsSets.results"));
	this.userDesignationError = element(by.binding('editCtrl.userDesignationError'));	
	this.permission_irf_view = element(by.binding('editCtrl.account.permission_irf_view'));
	this.permission_irf_add = element(by.binding('editCtrl.account.permission_irf_add'));
	this.permission_irf_edit = element(by.binding('editCtrl.account.permission_irf_edit'));
	this.permission_irf_delete = element(by.binding('editCtrl.account.permission_irf_delete'));
	this.permission_vif_view = element(by.binding('editCtrl.account.permission_vif_view'));
	this.permission_vif_add = element(by.binding('editCtrl.account.permission_vif_add'));
	this.permission_vif_edit = element(by.binding('editCtrl.account.permission_vif_edit'));
	this.permission_vif_delete = element(by.binding('editCtrl.account.permission_vif_delete'));
	this.permission_border_stations_view = element(by.binding('editCtrl.account.permission_border_stations_view'));
	this.permission_border_stations_add = element(by.binding('editCtrl.account.permission_border_stations_add'));               
	this.permission_border_stations_edit = element(by.binding('editCtrl.account.permission_border_stations_edit'));                
	this.permission_border_stations_delete = element(by.binding('editCtrl.account.permission_border_stations_delete'));                
	this.permission_accounts_manage = element(by.binding('editCtrl.account.permission_accounts_manage'));
	this.permission_receive_email = element(by.binding('editCtrl.account.permission_receive_email'));
	this.permission_vdc_manage = element(by.binding('editCtrl.account.permission_vdc_manage'));
	this.permission_budget_manage = element(by.binding('editCtrl.account.permission_budget_manage'));
	this.updateButton = element(by.binding('editCtrl.getUpdateButtonText'));
	
	
	this.navigateToPage = function() {
		return browser.get(constants.webAddress + '/accounts/create');
	}
	
	this.create = function() {
		return this.updateButton.click();
	}.bind(this);
	
	this.changeUserInfo = function() {
		var self = this;
		return this.firstName.clear().sendKeys(self.newFirstName).then(function() {
		 	return self.lastName.clear().sendKeys(self.newLastName);
		}).then(function() {
			return self.email.clear().sendKeys(self.newEmail);			
		}).then(function() {
			return self.userDesignationOptions.last().click();			
		});
	}.bind(this);
	
	this.clickAllPermissions = function(state) {
		var self = this;
		return this.permission_irf_view.click().then(function () {
			return self.permission_irf_add.click();
		}).then(function(){
			return self.permission_irf_edit.click();
		}).then(function(){
			return self.permission_irf_delete.click();			
		}).then(function(){
			return self.permission_vif_view.click();			
		}).then(function(){
			return self.permission_vif_add.click();				
		}).then(function(){
			return self.permission_vif_edit.click();			
		}).then(function(){
			return self.permission_vif_delete.click();			
		}).then(function(){
			return self.permission_border_stations_view.click();			
		}).then(function(){
			return self.permission_border_stations_add.click();
		}).then(function(){
			return self.permission_border_stations_edit.click();
		}).then(function(){
			return self.permission_border_stations_delete.click();
		}).then(function(){
			return self.permission_accounts_manage.click();
		}).then(function(){
			return self.permission_receive_email.click();
		}).then(function(){
			return self.permission_vdc_manage.click();
		}).then(function(){
			return self.permission_budget_manage.click();
		});		
	}.bind(this);

}

module.exports = new createAccountPage();