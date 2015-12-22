var c = require('../testConstants.json');
var loginPage = require('../accounts/loginPage.js');
var vifPage = require('../dataentry/vifPage.js');
var vifListPage = require('./vifList.page.js');
var methods = require('../commonMethods.js');


describe('Victim Interview Form List -', function() {
    var vifLPage = new vifListPage();

    beforeEach(function () {
        browser.ignoreSynchronization = true;
    });

    it("setup", function(){
        loginPage.loginAsAdmin();
        vifPage.createVif();
        browser.sleep(1000);
        vifPage.filloutVif('BHD100');
        browser.sleep(1000);
        vifPage.createVif();
        browser.sleep(1000);
        vifPage.filloutVif('DNG200');
        browser.sleep(1000);
    });

    it('Has an input vif button', function () {
        browser.driver.get(c.webAddress + "/data-entry/vifs/");
        browser.sleep(1000);
        expect(vifLPage.newvifButton.isPresent()).toBe(true);
    });

    it('Has an export as CSV button', function () {
        browser.driver.get(c.webAddress + "/data-entry/vifs/");
        browser.sleep(1000);
        expect(vifLPage.exportButton.isPresent()).toBe(true);
    });

    it('Can filter by Name', function () {
        browser.driver.get(c.webAddress + "/data-entry/vifs/");
        browser.sleep(1000);
        var firstCat = element(by.repeater('vif in vm.vifs').row(1));
        vifLPage.vifNumberHeader.click();
        browser.sleep(1000);
        var secondCat = element(by.repeater('vif in vm.vifs').row(1));
        expect(firstCat).not.toEqual(secondCat); // We know our new address name will be on top
    });

    it('Can paginate by another value', function () {
        browser.driver.get(c.webAddress + "/data-entry/vifs/");
        browser.sleep(1000);
        browser.findElement(protractor.By.css('select option:nth-child(2)')).click();
    });

    it('Can search by vif Number', function () {
        browser.driver.get(c.webAddress + "/data-entry/vifs/");
        vifLPage.search("BHD");
        browser.sleep(500);
        var firstBookName = element(by.repeater('vif in vm.vifs').row(0).column('vif.vif_number'));
        expect(firstBookName.getText()).toBe("BHD100");
    });

    it('Can Delete VIFs', function () {
        browser.driver.get(c.webAddress + "/data-entry/vifs/");
        var vifToDelete = element(by.partialLinkText("Delete"));
        methods.click(vifToDelete);
        var confirmDelete = element(by.partialLinkText("Confirm"));
        methods.click(confirmDelete);

        var vifToDelete = element(by.partialLinkText("Delete"));
        methods.click(vifToDelete);
        var confirmDelete = element(by.partialLinkText("Confirm"));
        methods.click(confirmDelete);
    });
});


