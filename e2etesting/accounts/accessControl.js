var constants = require('../testConstants.json');

var accessControlPage = function () {
	
	this.updateButton = element(by.buttonText('Update'));
	this.accounts = element.all(by.repeater("account in accessCtrl.accounts.results"))
	this.firstUserIrfAdd = this.accounts.first().element(by.binding('account.permission_irf_add ? "Yes" : "No" '));
	this.firstUserIrfDelete = this.accounts.first().element(by.binding('account.permission_irf_delete ? "Yes" : "No" '));
	this.firstUserIrfEdit = this.accounts.first().element(by.binding('account.permission_irf_edit ? "Yes" : "No" '));
	this.firstUserIrfView = this.accounts.first().element(by.binding('account.permission_irf_view ? "Yes" : "No" '));
	
	this.firstUserVifAdd = this.accounts.first().element(by.binding('account.permission_vif_add ? "Yes" : "No" '));
	this.firstUserVifDelete = this.accounts.first().element(by.binding('account.permission_vif_delete ? "Yes" : "No" '));
	this.firstUserVifEdit = this.accounts.first().element(by.binding('account.permission_vif_edit ? "Yes" : "No" '));
	this.firstUserVifView = this.accounts.first().element(by.binding('account.permission_vif_view ? "Yes" : "No" '));
	
	this.firstUserBorderStationAdd = this.accounts.first().element(by.binding('account.permission_border_stations_add ? "Yes" : "No" '))
	this.firstUserBorderStationDelete = this.accounts.first().element(by.binding('account.permission_border_stations_delete ? "Yes" : "No" '))
	this.firstUserBorderStationEdit = this.accounts.first().element(by.binding('account.permission_border_stations_edit ? "Yes" : "No" '))
	this.firstUserBorderStationView = this.accounts.first().element(by.binding('account.permission_border_stations_view ? "Yes" : "No" '))
	
	this.firstUserAccountsManage = this.accounts.first().element(by.binding('account.permission_accounts_manage ? "Yes" : "No" '))
	this.firstUserReceiveMail = this.accounts.first().element(by.binding('account.permission_receive_email ? "Yes" : "No" '))
	this.firstUserVdcManage = this.accounts.first().element(by.binding('account.permission_vdc_manage ? "Yes" : "No" '))
	this.firstUserBudgetManage = this.accounts.first().element(by.binding('account.permission_budget_manage ? "Yes" : "No" '))
	
	this.navigateToPage = function(){
		//Call a get request to navigate to the specific page desired.
		return browser.get(constants.webAddress + '/accounts/access-control');
	}
	
}

module.exports = new accessControlPage();


//Remember this code:this.permission_irf_view.click()