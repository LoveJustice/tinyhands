var loginPage = require('./loginPage');
var createAccountPage = require('./createAccountPage');
var constants = require('../testConstants.json');


describe('Create Account Page', function() {
	
	beforeAll(function () {
		browser.ignoreSynchronization=true;
		loginPage.loginAsAdmin();
		createAccountPage.navigateToPage();
		browser.waitForAngular();
	});
	
	describe('when first loaded', function() {		
		it('should have user information fields blank', function() {	
			expect(createAccountPage.firstName.getAttribute('value')).toEqual('');
			expect(createAccountPage.lastName.getAttribute('value')).toEqual('');
			expect(createAccountPage.email.getAttribute('value')).toEqual('');
			expect(createAccountPage.userDesignation.getAttribute('value')).toEqual('?');
		});
		
		it('should have permissions set to No', function() {
			
			for(permission in createAccountPage.permissions) {
                if (createAccountPage.permissions.hasOwnProperty(permission)) {
                    expect(createAccountPage.permissions[permission].getText()).toEqual('No');
                }
            }				
		});
		
		it("should have correct title", function() {
			expect(createAccountPage.title.getText()).toEqual('Create Account');
		});
		
		it("should have correct button text", function() {
			expect(createAccountPage.updateButton.getText()).toEqual('Create');
		});
		
		it("should allow permissions to change individually", function() {
			createAccountPage.clickAllPermissions();
			
			for(permission in createAccountPage.permissions) {
                if (createAccountPage.permissions.hasOwnProperty(permission)) {
                    expect(createAccountPage.permissions[permission].getText()).toEqual('Yes');
                }
            }	
		});
	});	
	
	describe('when creating', function() {
		
		beforeAll(function() {
			browser.ignoreSynchronization=true;
			createAccountPage.navigateToPage();
			browser.waitForAngular();
		});
		
		it('should show error when email is not valid', function() {
			createAccountPage.create()
			.then(function() {
				expect(createAccountPage.emailError.getText()).toEqual('An email is required.');
			})
			.then(function() {
				expect(createAccountPage.userDesignationError.getText()).toEqual('A user designation is required.');
			});;					
		});
		
		it('should redirect to accounts page', function() {
			createAccountPage.changeUserInfo()
			.then(function() {
				return createAccountPage.create();
			}).then(function() {
				return browser.waitForAngular();
			}).then(function() {
				return browser.driver.wait(function() {
					return browser.getCurrentUrl().then(function(url) {						
						return url != constants.webAddress + '/accounts/create/';
					});
				}, 2000);
			}).then(function() {
				expect(browser.getCurrentUrl()).toEqual(constants.webAddress + '/accounts/');												
			});
		});
	});
});