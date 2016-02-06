var c = require('../testConstants.json');
var loginPage = require('../accounts/loginPage.js');

describe('TinyHands Address1s - ', function () {
    var newAddressName = "aaaaa new Address 1";

    beforeEach(function () {
        return browser.ignoreSynchronization = true;
    });

    it('should navigate to address1 manage page', function () {
        loginPage.logout();
        loginPage.loginAsAdmin();
        browser.get(c.webAddress + '/data-entry/geocodelocations/district-admin/');
        expect(browser.getTitle()).toContain('Manage Address 1');
    });

    it('should be able to edit the first address name', function () {

        browser.sleep(1000);
        element.all(by.className("edit")).first().click();
        browser.sleep(1000);

        element(by.id('addressName')).clear().sendKeys(newAddressName);
        browser.sleep(500);
        element(by.buttonText('Save')).click();


        browser.sleep(1000);
        browser.driver.navigate().refresh();
        browser.sleep(1000);

        var item = element(by.xpath("//td[text() = '" + newAddressName + "']"));

        expect(item.getText()).toEqual(newAddressName);
        browser.sleep(500);
    });

    it('should be able to be filtered by the address name', function () {
        element(by.id("addressNameHeader")).click();
        browser.sleep(500);
        var lastAddress = element.all(by.className("address-name")).first();
        browser.sleep(1000);
        expect(lastAddress.getText()).not.toEqual(newAddressName); // We know our new address name will be on top
    });

    it('should be able to be paginated by a different number', function () {
        element(by.cssContainingText('option', '50')).click();
        expect(element(by.model('vm.paginateBy')).isPresent()).toBe(true);
    });

    it('should be able to search', function () {
        element(by.model('vm.searchValue')).clear().sendKeys("Baglung").then(function (){
            element(by.linkText('Search')).click();
        }).then(function () {
            browser.sleep(500);
            expect(element.all(by.className('address-name')).first().getText()).toBe("Baglung");
        });
    });
});
