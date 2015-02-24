var constants = require('../testConstants.json');
var loginPage = require('../accounts/loginPage.js');
var vdcAdminPage = require('./vdcAdminPage.js');

describe('TinyHands Login', function () {
    beforeEach(function () {
        return browser.ignoreSynchronization = true;
    });

    it('should navigate to VDC manage page', function () {
        loginPage.logout();
        loginPage.loginAsAdmin();
        vdcAdminPage.navigate();
        expect(browser.getTitle()).toContain('Manage VDCs');
    });

    it('should first VDCs information', function () {
        vdcAdminPage.firstVdcEditButton.click();
        //browser.sleep(6000);
        //vdcAdminPage.changeValues();
        //vdcAdminPage.checkIfVdcUpdated();
    });

});
