var c = require('../testConstants.json');
var loginPage = require('../accounts/loginPage.js');
var dynStationWindow = require('./dynStationWindow.js');

describe('Dynamic Station Window', function() {

    beforeEach(function () {
        return browser.ignoreSynchronization = true;
    });

    describe('Dynamic Station Window Tests', function () {
        it('accepts credentials', function () {
            loginPage.logout();
            loginPage.loginAsAdmin();
            browser.sleep(1000);
        });
    });
});
