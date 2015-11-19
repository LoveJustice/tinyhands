var loginPage = require('./loginPage');
var accessControlPage = require('./accessControl');
var constants = require('../testConstants.json');

describe('Access Control Page', function() {
	
	beforeAll(function () {
		browser.ignoreSynchronization=true;
		loginPage.loginAsAdmin();
		browser.ignoreSynchronization=false;
		accessControlPage.navigateToPage();
	});
	
	describe('When the irf permission buttons are clicked',function(){
		it('should change the irf permissions', function(){
			//figure out the state of the button
			var initialIrfAdd = accessControlPage.firstUserIrfAdd.getText();
			var initialIrfDelete = accessControlPage.firstUserIrfDelete.getText();
			var initialIrfEdit = accessControlPage.firstUserIrfEdit.getText();
			var initialIrfView = accessControlPage.firstUserIrfView.getText();
			
			//click the button
			accessControlPage.firstUserIrfAdd.click();
			accessControlPage.firstUserIrfDelete.click();
			accessControlPage.firstUserIrfEdit.click();
			accessControlPage.firstUserIrfView.click();
			
			//expect the button state to change.
			expect(accessControlPage.firstUserIrfAdd.getText()).not.toEqual(initialIrfAdd);
			expect(accessControlPage.firstUserIrfDelete.getText()).not.toEqual(initialIrfDelete);
			expect(accessControlPage.firstUserIrfEdit.getText()).not.toEqual(initialIrfEdit);
			expect(accessControlPage.firstUserIrfView.getText()).not.toEqual(initialIrfView);
			
			
			
		});
	});
	
	describe('When the vif permission buttons are clicked',function(){
		it('should change the vif permissions', function(){
			//figure out the state of the button
			var initialVifAdd = accessControlPage.firstUserVifAdd.getText();
			var initialVifDelete = accessControlPage.firstUserVifDelete.getText();
			var initialVifEdit = accessControlPage.firstUserVifEdit.getText();
			var initialVifView = accessControlPage.firstUserVifView.getText();
			
			//click the button
			accessControlPage.firstUserVifAdd.click();
			accessControlPage.firstUserVifDelete.click();
			accessControlPage.firstUserVifEdit.click();
			accessControlPage.firstUserVifView.click();
			
			//expect the button state to change.
			expect(accessControlPage.firstUserVifAdd.getText()).not.toEqual(initialVifAdd);
			expect(accessControlPage.firstUserVifDelete.getText()).not.toEqual(initialVifDelete);
			expect(accessControlPage.firstUserVifEdit.getText()).not.toEqual(initialVifEdit);
			expect(accessControlPage.firstUserVifView.getText()).not.toEqual(initialVifView);
			

		});
	});
	
	
	describe('When the border station permission buttons are clicked',function(){
		it('should change the border station permissions', function(){

			var initialBorderStationAdd = accessControlPage.firstUserBorderStationAdd.getText();
			var initialBorderStationDelete = accessControlPage.firstUserBorderStationDelete.getText();
			var initialBorderStationEdit = accessControlPage.firstUserBorderStationEdit.getText();
			var initialBorderStationView = accessControlPage.firstUserBorderStationView.getText();
			
	
			accessControlPage.firstUserBorderStationAdd.click();
			accessControlPage.firstUserBorderStationDelete.click();
			accessControlPage.firstUserBorderStationEdit.click();
			accessControlPage.firstUserBorderStationView.click();
			
		
			expect(accessControlPage.firstUserBorderStationAdd.getText()).not.toEqual(initialBorderStationAdd);
			expect(accessControlPage.firstUserBorderStationDelete.getText()).not.toEqual(initialBorderStationDelete);
			expect(accessControlPage.firstUserBorderStationEdit.getText()).not.toEqual(initialBorderStationEdit);
			expect(accessControlPage.firstUserBorderStationView.getText()).not.toEqual(initialBorderStationView);
			

		});
	});
	
	
	describe('When the last few misc permission buttons are clicked',function(){
		it('should change the last few misc permissions', function(){
			//figure out the state of the button
			var initialAccountsManage = accessControlPage.firstUserAccountsManage.getText();
			var initialReceiveMail = accessControlPage.firstUserReceiveMail.getText();
			var initialVdcManage = accessControlPage.firstUserVdcManage.getText();
			var initialBudgetManage = accessControlPage.firstUserBudgetManage.getText();
			
			//click the button
			accessControlPage.firstUserAccountsManage.click();
			accessControlPage.firstUserReceiveMail.click();
			accessControlPage.firstUserVdcManage.click();
			accessControlPage.firstUserBudgetManage.click();
			
			//expect the button state to change.
			expect(accessControlPage.firstUserAccountsManage.getText()).not.toEqual(initialAccountsManage);
			expect(accessControlPage.firstUserReceiveMail.getText()).not.toEqual(initialReceiveMail);
			expect(accessControlPage.firstUserVdcManage.getText()).not.toEqual(initialVdcManage);
			expect(accessControlPage.firstUserBudgetManage.getText()).not.toEqual(initialBudgetManage);
			

		});
	});
	
	
});