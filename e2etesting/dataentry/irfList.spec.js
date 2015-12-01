var c = require('../testConstants.json');
var loginPage = require('../accounts/loginPage.js');
var irfPage = require('../dataentry/irfCRUD.js');
var irfListPage = require('./irfList.page.js');
var methods = require('../commonMethods.js');


describe('Interception Record Form List -', function() {
    var irfList = new irfListPage();

    beforeEach(function () {
        browser.ignoreSynchronization = true;
    });

    it("setup", function(){
        loginPage.loginAsAdmin();
        irfPage.getToIRF();
        irfPage.fillOutIRF('BHD100');
        irfPage.getToIRF();
        irfPage.fillOutIRF('DNG200');
    });

    it('Has an input IRF button', function () {
        browser.driver.get(c.webAddress + "/data-entry/irfs/");
        expect(irfList.newIrfButton.isPresent()).toBe(true);
    });

    it('Has an export as CSV button', function () {
        browser.driver.get(c.webAddress + "/data-entry/irfs/");
        expect(irfList.exportButton.isPresent()).toBe(true);
    });

    it('Can filter by Name', function () {
        browser.driver.get(c.webAddress + "/data-entry/irfs/");
        var firstCat = element(by.repeater('irf in vm.irfs').row(1));
        irfList.irfNumberHeader.click();
        var secondCat = element(by.repeater('irf in vm.irfs').row(1));
        expect(firstCat).not.toEqual(secondCat); // We know our new address name will be on top
    });

    it('Can paginate by another value', function () {
        browser.driver.get(c.webAddress + "/data-entry/irfs/");
        browser.findElement(protractor.By.css('select option:nth-child(2)')).click();
    });

    it('Can search by IRF Number', function () {
        browser.driver.get(c.webAddress + "/data-entry/irfs/");
        irfList.search("BHD");
        browser.sleep(500);
        var firstBookName = element(by.repeater('irf in vm.irfs').row(0).column('irf.irf_number'));
        expect(firstBookName.getText()).toBe("BHD100");
    });


    it('Can Delete IRFs', function () {
        browser.get(c.webAddress + '/data-entry/irfs/');

        var dIRF = element(by.partialLinkText("Delete"));
        methods.click(dIRF);
        var confirmDelete = element(by.partialLinkText("Confirm"));
        methods.click(confirmDelete);

        var dIRF = element(by.partialLinkText("Delete"));
        methods.click(dIRF);
        var confirmDelete = element(by.partialLinkText("Confirm"));
        methods.click(confirmDelete);
    });
});


