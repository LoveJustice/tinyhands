var loginPage = require('./loginPage');
var editAccountPage = require('./editAccountPage');
var constants = require('../testConstants.json');


describe('Edit Account Page', function() {
	
	beforeAll(function () {
		browser.ignoreSynchronization=true;
		loginPage.loginAsAdmin();
		browser.ignoreSynchronization=false;		
		editAccountPage.navigateToPage();
	});
	
	describe('when first loaded', function() {		
		it('should have user information field populated', function() {	
			expect(editAccountPage.firstName.getAttribute('value')).toEqual(constants.fooFirstName);
			expect(editAccountPage.lastName.getAttribute('value')).toEqual(constants.fooLastName);
			expect(editAccountPage.email.getAttribute('value')).toEqual(constants.fooEmail);
			expect(editAccountPage.userDesignation.getAttribute('value')).toEqual("0");
		});
		
		it('should have permissions set', function() {
			for(permission in editAccountPage.permissions) {
                if (editAccountPage.permissions.hasOwnProperty(permission)) {
                    expect(editAccountPage.permissions[permission].getText()).toEqual('Yes');
                }
            }								
		});
		
		it("should have user's name in title", function() {
			expect(editAccountPage.title.getText()).toEqual('Edit ' + constants.fooFirstName + ' ' + constants.fooLastName + "'s Account");
		});
		
		it("should have correct button text", function() {
			expect(editAccountPage.updateButton.getText()).toEqual('Update');
		});
		
		it("should allow permissions to change individually", function() {
			editAccountPage.clickAllPermissions();
			
			for(permission in editAccountPage.permissions) {
                if (editAccountPage.permissions.hasOwnProperty(permission)) {
                    expect(editAccountPage.permissions[permission].getText()).toEqual('No');
                }
            }
		})
	});	
	
	describe('when updating', function() {
		
		beforeAll(function() {
			browser.ignoreSynchronization=true;
			editAccountPage.navigateToPage();
			browser.waitForAngular();
		});
		
		it('should show error when email is not valid', function() {
			editAccountPage.clearEmailField()
			.then(editAccountPage.update)
			.then(function() {
				expect(editAccountPage.emailError.getText()).toEqual('An email is required.');
			});					
		});
		
		it('should redirect to accounts page', function() {
			editAccountPage.changeUserInfo()
			.then(editAccountPage.update)
			.then(function() {
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
				expect(editAccountPage.firstName.getAttribute('value')).toEqual(editAccountPage.newFirstName);
				expect(editAccountPage.lastName.getAttribute('value')).toEqual(editAccountPage.newLastName);
				expect(editAccountPage.email.getAttribute('value')).toEqual(editAccountPage.newEmail);
				expect(editAccountPage.userDesignation.getAttribute('value')).toEqual("3");
				
				for(permission in editAccountPage.permissions) {
					if (editAccountPage.permissions.hasOwnProperty(permission)) {
						expect(editAccountPage.permissions[permission].getText()).toEqual('No');
					}
				}
			});
		});
	});
});