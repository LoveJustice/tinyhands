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
        browser.sleep(500);
        vdcAdminPage.changeValues();
        browser.sleep(500);

        browser.get(constants.webAddress);
        vdcAdminPage.navigate();
        browser.sleep(500);

        expect(element(by.css(".vdc_admin_name")).getText()).toBe(constants.vdcNewName);
        expect(element.all(by.css(".vdc_admin_district")).first().getText()).toEqual(constants.vdcNewDis);
        expect(element.all(by.css(".vdc_admin_cannonical")).first().getText()).toEqual(constants.vdcNewCan);
    });

});
