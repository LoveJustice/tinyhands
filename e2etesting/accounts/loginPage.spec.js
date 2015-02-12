var constants = require('../testConstants.json');
var loginPage = require('./loginPage.js');

describe('TinyHands Login', function() {

    beforeEach(function() {
      return browser.ignoreSynchronization = true;
    });

    it('should have a title', function() {
        browser.get('http://0.0.0.0:8000/logout/');
	    expect(browser.getTitle()).toContain('Log In');
    });



    describe('admin can login', function() {
      it('accepts credentials', function() {
        loginPage.logout();
        loginPage.loginAsAdmin();

        expect(browser.driver.getCurrentUrl()).toContain('portal/dashboard');

      });
    });

    describe('admin can logout', function() {
      it('accepts credentials', function() {
        loginPage.logout();
        expect(browser.driver.getTitle()).toContain('Log In');
      });
    });

});
