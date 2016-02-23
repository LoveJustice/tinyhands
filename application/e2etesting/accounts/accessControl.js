var constants = require('../testConstants.json');

var accessControlPage = function () {

	this.updateButton = element(by.buttonText('Update'));
	this.accounts = element.all(by.repeater("account in accessCtrl.accounts.results"));
	this.firstUserIrfAdd = this.accounts.first().element(by.binding('account.permission_irf_add ? "Yes" : "No" '));
	this.firstUserIrfDelete = this.accounts.first().element(by.binding('account.permission_irf_delete ? "Yes" : "No" '));
	this.firstUserIrfEdit = this.accounts.first().element(by.binding('account.permission_irf_edit ? "Yes" : "No" '));
	this.firstUserIrfView = this.accounts.first().element(by.binding('account.permission_irf_view ? "Yes" : "No" '));

	this.firstUserVifAdd = this.accounts.first().element(by.binding('account.permission_vif_add ? "Yes" : "No" '));
	this.firstUserVifDelete = this.accounts.first().element(by.binding('account.permission_vif_delete ? "Yes" : "No" '));
	this.firstUserVifEdit = this.accounts.first().element(by.binding('account.permission_vif_edit ? "Yes" : "No" '));
	this.firstUserVifView = this.accounts.first().element(by.binding('account.permission_vif_view ? "Yes" : "No" '));

	this.firstUserBorderStationAdd = this.accounts.first().element(by.binding('account.permission_border_stations_add ? "Yes" : "No" '));
	this.firstUserBorderStationDelete = this.accounts.first().element(by.binding('account.permission_border_stations_delete ? "Yes" : "No" '));
	this.firstUserBorderStationEdit = this.accounts.first().element(by.binding('account.permission_border_stations_edit ? "Yes" : "No" '));
	this.firstUserBorderStationView = this.accounts.first().element(by.binding('account.permission_border_stations_view ? "Yes" : "No" '));

	this.firstUserAccountsManage = this.accounts.first().element(by.binding('account.permission_accounts_manage ? "Yes" : "No" '));
	this.firstUserReceiveMail = this.accounts.first().element(by.binding('account.permission_receive_email ? "Yes" : "No" '));
	this.firstUserAddress2Manage = this.accounts.first().element(by.binding('account.permission_address2_manage ? "Yes" : "No" '));
	this.firstUserBudgetManage = this.accounts.first().element(by.binding('account.permission_budget_manage ? "Yes" : "No" '));

	this.firstUserDesignation = this.accounts.first().element(by.model('accessCtrl.account.user_designation'));
	this.firstUserDesignationOptions = this.accounts.first().all(by.options('p.id as p.name for p in accessCtrl.permissions.results'));

	this.navigateToPage = function(){
		//Call a get request to navigate to the specific page desired.
		return browser.get(constants.webAddress + '/accounts/access-control');
	}

	this.getTestUserAccountRow = function() {
		return this.accounts.filter(function(elem, index) {
			return elem.element(by.binding('account.first_name+" "+account.last_name')).getText().then(function(text) {
				return text === "test user";
			});
		}).then(function(filteredAccounts) {
			return populateAccountRow(filteredAccounts[0]);
		});
	}.bind(this);

	function populateAccountRow(accountRow){
		var account = {};
		account.self = accountRow;
		account.irfView = accountRow.element(by.binding('account.permission_irf_view ? "Yes" : "No" '));
		account.irfAdd = accountRow.element(by.binding('account.permission_irf_add ? "Yes" : "No" '));
		account.irfEdit = accountRow.element(by.binding('account.permission_irf_edit ? "Yes" : "No" '));
		account.irfDelete = accountRow.element(by.binding('account.permission_irf_delete ? "Yes" : "No" '));
		account.vifView = accountRow.element(by.binding('account.permission_vif_view ? "Yes" : "No" '));
		account.vifAdd = accountRow.element(by.binding('account.permission_vif_add ? "Yes" : "No" '));
		account.vifEdit = accountRow.element(by.binding('account.permission_vif_edit ? "Yes" : "No" '));
		account.vifDelete = accountRow.element(by.binding('account.permission_vif_delete ? "Yes" : "No" '));
		account.borderStationView = accountRow.element(by.binding('account.permission_border_stations_view ? "Yes" : "No" '));
		account.borderStationAdd = accountRow.element(by.binding('account.permission_border_stations_add ? "Yes" : "No" '));
		account.borderStationEdit = accountRow.element(by.binding('account.permission_border_stations_edit ? "Yes" : "No" '));
		account.borderStationDelete = accountRow.element(by.binding('account.permission_border_stations_delete ? "Yes" : "No" '));
		account.accountsManage = accountRow.element(by.binding('account.permission_accounts_manage ? "Yes" : "No" '));
		account.receiveEmail = accountRow.element(by.binding('account.permission_receive_email ? "Yes" : "No" '));
		account.address2Manage = accountRow.element(by.binding('account.permission_address2_manage ? "Yes" : "No" '));
		account.BudgetManage = accountRow.element(by.binding('account.permission_budget_manage ? "Yes" : "No" '));
		return account;
	}
}

module.exports = new accessControlPage();


//Remember this code:this.permission_irf_view.click()
