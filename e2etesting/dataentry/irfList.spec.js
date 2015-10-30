var c = require('../testConstants.json');
var loginPage = require('../accounts/loginPage.js');
var irfListPage = require('./irfList.page.js');

describe('Interception Record Form List -', function() {
    var irfList = new irfListPage();

    beforeEach(function () {
        browser.ignoreSynchronization = true;
    });

    it("setup", function(){
        loginPage.loginAsAdmin();
    });

    it('Has an input IRF button', function () {
        browser.driver.get(c.webAddress + "/data-entry/irfs/").then(function(){
            expect(irfList.newIrfButton.isPresent()).toBe(true);
        });
    });

    it('Has an export as CSV button', function () {
        browser.driver.get(c.webAddress + "/data-entry/irfs/").then(function(){
            expect(irfList.exportButton.isPresent()).toBe(true);
        });
    });

    it('Has an export as CSV button', function () {
        browser.driver.get(c.webAddress + "/data-entry/irfs/").then(function(){
            irfList.irfNumberHeader.click();
        });
    });
});


