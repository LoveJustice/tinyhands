var loginPage = require('./loginPage');
var editAccountPage = require('./editAccountPage');
var constants = require('../testConstants.json');


describe('Edit Account Page', function() {
	
	beforeAll(function () {
		browser.ignoreSynchronization=true;
		loginPage.loginAsAdmin();
		editAccountPage.navigateToPage();
		browser.waitForAngular();
	});
	
	describe('when first loaded', function() {		
		it('should have user information field populated', function() {	
			expect(editAccountPage.firstName.getAttribute('value')).toEqual(constants.fooFirstName);
			expect(editAccountPage.lastName.getAttribute('value')).toEqual(constants.fooLastName);
			expect(editAccountPage.email.getAttribute('value')).toEqual(constants.fooEmail);
			expect(editAccountPage.userDesignation.getAttribute('value')).toEqual("0");
		});
		
		it('should have permissions set', function() {
			expect(editAccountPage.permission_irf_view.getText()).toEqual('Yes');
			expect(editAccountPage.permission_irf_add.getText()).toEqual('Yes');
			expect(editAccountPage.permission_irf_edit.getText()).toEqual('Yes');
			expect(editAccountPage.permission_irf_delete.getText()).toEqual('Yes');
			expect(editAccountPage.permission_vif_view.getText()).toEqual('Yes');
			expect(editAccountPage.permission_vif_add.getText()).toEqual('Yes');
			expect(editAccountPage.permission_vif_edit.getText()).toEqual('Yes');
			expect(editAccountPage.permission_vif_delete.getText()).toEqual('Yes');
			expect(editAccountPage.permission_border_stations_view.getText()).toEqual('Yes');			
			expect(editAccountPage.permission_border_stations_add.getText()).toEqual('Yes');			
			expect(editAccountPage.permission_border_stations_edit.getText()).toEqual('Yes');			
			expect(editAccountPage.permission_border_stations_delete.getText()).toEqual('Yes');
			expect(editAccountPage.permission_accounts_manage.getText()).toEqual('Yes');			
			expect(editAccountPage.permission_receive_email.getText()).toEqual('Yes');			
			expect(editAccountPage.permission_vdc_manage.getText()).toEqual('Yes');			
			expect(editAccountPage.permission_budget_manage.getText()).toEqual('Yes');							
		});
		
		it("should have user's name in title", function() {
			expect(editAccountPage.title.getText()).toEqual('Edit ' + constants.fooFirstName + ' ' + constants.fooLastName + "'s Account");
		});
		
		it("should have correct button text", function() {
			expect(editAccountPage.updateButton.getText()).toEqual('Update');
		});
		
		it("should allow permissions to change individually", function() {
			editAccountPage.clickAllPermissions();
			
			expect(editAccountPage.permission_irf_view.getText()).toEqual('No');
			expect(editAccountPage.permission_irf_add.getText()).toEqual('No');
			expect(editAccountPage.permission_irf_edit.getText()).toEqual('No');
			expect(editAccountPage.permission_irf_delete.getText()).toEqual('No');
			expect(editAccountPage.permission_vif_view.getText()).toEqual('No');
			expect(editAccountPage.permission_vif_add.getText()).toEqual('No');
			expect(editAccountPage.permission_vif_edit.getText()).toEqual('No');
			expect(editAccountPage.permission_vif_delete.getText()).toEqual('No');
			expect(editAccountPage.permission_border_stations_view.getText()).toEqual('No');			
			expect(editAccountPage.permission_border_stations_add.getText()).toEqual('No');			
			expect(editAccountPage.permission_border_stations_edit.getText()).toEqual('No');			
			expect(editAccountPage.permission_border_stations_delete.getText()).toEqual('No');
			expect(editAccountPage.permission_accounts_manage.getText()).toEqual('No');			
			expect(editAccountPage.permission_receive_email.getText()).toEqual('No');			
			expect(editAccountPage.permission_vdc_manage.getText()).toEqual('No');			
			expect(editAccountPage.permission_budget_manage.getText()).toEqual('No');
		})
	});	
	
	describe('when updating', function() {
		
		beforeAll(function() {
			browser.ignoreSynchronization=true;
			editAccountPage.navigateToPage();
			browser.waitForAngular();
			editAccountPage.changeUserInfo();							
		});
		
		it('should redirect to accounts page', function() {
			editAccountPage.update().then(function() {
				return browser.waitForAngular();							
			}).then(function() {
				browser.sleep(1000);
				expect(browser.getCurrentUrl()).toEqual(constants.webAddress + '/accounts/');				
			});
		});
		
		it('should update account fields', function() {
			editAccountPage.navigateToPage().then(function() {
				return browser.waitForAngular();					
			}).then(function() {
				expect(editAccountPage.permission_irf_view.getText()).toEqual('No');
				expect(editAccountPage.permission_irf_add.getText()).toEqual('No');
				expect(editAccountPage.permission_irf_edit.getText()).toEqual('No');
				expect(editAccountPage.permission_irf_delete.getText()).toEqual('No');
				expect(editAccountPage.permission_vif_view.getText()).toEqual('No');
				expect(editAccountPage.permission_vif_add.getText()).toEqual('No');
				expect(editAccountPage.permission_vif_edit.getText()).toEqual('No');
				expect(editAccountPage.permission_vif_delete.getText()).toEqual('No');
				expect(editAccountPage.permission_border_stations_view.getText()).toEqual('No');			
				expect(editAccountPage.permission_border_stations_add.getText()).toEqual('No');			
				expect(editAccountPage.permission_border_stations_edit.getText()).toEqual('No');			
				expect(editAccountPage.permission_border_stations_delete.getText()).toEqual('No');
				expect(editAccountPage.permission_accounts_manage.getText()).toEqual('No');			
				expect(editAccountPage.permission_receive_email.getText()).toEqual('No');			
				expect(editAccountPage.permission_vdc_manage.getText()).toEqual('No');			
				expect(editAccountPage.permission_budget_manage.getText()).toEqual('No');
			});
		});
	});
});