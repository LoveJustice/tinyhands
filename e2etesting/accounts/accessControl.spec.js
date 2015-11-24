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
	
	describe('On page load', function() {
		it('should have user account', function() {
			accessControlPage.getTestUserAccountRow().then(function(testUser) {
				expect(testUser.irfView.getText()).toEqual("Yes");
				expect(testUser.irfAdd.getText()).toEqual("Yes");
				expect(testUser.irfEdit.getText()).toEqual("Yes");
				expect(testUser.irfDelete.getText()).toEqual("Yes");
				expect(testUser.vifView.getText()).toEqual("Yes");
				expect(testUser.vifAdd.getText()).toEqual("Yes");
				expect(testUser.vifEdit.getText()).toEqual("Yes");
				expect(testUser.vifDelete.getText()).toEqual("Yes");
				expect(testUser.borderStationView.getText()).toEqual("Yes");
				expect(testUser.borderStationAdd.getText()).toEqual("Yes");
				expect(testUser.borderStationEdit.getText()).toEqual("Yes");
				expect(testUser.borderStationDelete.getText()).toEqual("Yes");
				expect(testUser.accountsManage.getText()).toEqual("Yes");
				expect(testUser.receiveEmail.getText()).toEqual("Yes");
				expect(testUser.vdcManage.getText()).toEqual("Yes");
				expect(testUser.BudgetManage.getText()).toEqual("Yes");		
			});
		});
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
	
	
	describe("When the user changes a profile's designation", function(){
		it('should change the last few misc permissions to match', function(){
			//First set the designation to a default value like summer intern
			//Assumes that the testing account is designated as a super admin.
			
			
		accessControlPage.firstUserDesignationOptions.filter(function(elem, idx){
			return elem.getText().then(function(text){
				return text=="Summer Intern";
			});
		 }).then(function(filteredOptions){

			 return filteredOptions[0].click();
		 }); 
			expect(accessControlPage.firstUserVifAdd.getText()).toEqual("No");
			expect(accessControlPage.firstUserVifDelete.getText()).toEqual("No");
			expect(accessControlPage.firstUserVifEdit.getText()).toEqual("No");
			expect(accessControlPage.firstUserVifView.getText()).toEqual("Yes");
			
			
			expect(accessControlPage.firstUserIrfAdd.getText()).toEqual("No");
			expect(accessControlPage.firstUserIrfDelete.getText()).toEqual("No");
			expect(accessControlPage.firstUserIrfEdit.getText()).toEqual("No");
			expect(accessControlPage.firstUserIrfView.getText()).toEqual("Yes");
			
			expect(accessControlPage.firstUserBorderStationAdd.getText()).toEqual("Yes");
			expect(accessControlPage.firstUserBorderStationDelete.getText()).toEqual("No");
			expect(accessControlPage.firstUserBorderStationEdit.getText()).toEqual("Yes");
			expect(accessControlPage.firstUserBorderStationView.getText()).toEqual("Yes");
			
			expect(accessControlPage.firstUserAccountsManage.getText()).toEqual("No");
			expect(accessControlPage.firstUserReceiveMail.getText()).toEqual("No");
			expect(accessControlPage.firstUserVdcManage.getText()).toEqual("Yes");
			expect(accessControlPage.firstUserBudgetManage.getText()).toEqual("No");
			
			
			
		
			
		});		
	});
	
	
	
	
});