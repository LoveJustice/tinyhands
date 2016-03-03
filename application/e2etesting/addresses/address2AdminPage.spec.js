var constants = require('../testConstants.json');
var loginPage = require('../accounts/loginPage.js');
var address2AdminPage = require('./address2AdminPage.js');

describe('TinyHands Address2s', function () {
    beforeEach(function () {
        return browser.ignoreSynchronization = true;
    });

    it('should navigate to Address2 manage page', function () {
        loginPage.logout();
        loginPage.loginAsAdmin();
        address2AdminPage.navigate();
        expect(browser.getTitle()).toContain('Manage');
    });

    it('should change the first Address2s information', function () {
        browser.ignoreSynchronization = false;
        browser.sleep(500);

        //browser.pause();

        element.all(by.className("edit")).first().click();
        browser.sleep(500);
        //browser.ignoreSynchronization = false;
        address2AdminPage.changeValues();
        browser.ignoreSynchronization = true;
        browser.sleep(1000);
        browser.get(constants.webAddress);
        address2AdminPage.navigate();


        browser.sleep(1000);
        var item = element(by.xpath("//td[text() = '" + constants.address2EditName + "']"));
        var address1 = item.element(by.xpath("../td[4]"));
        var cannon = item.element(by.xpath("../td[5]"));

        expect(item.getText()).toEqual(constants.address2EditName);
        expect(address1.getText()).toEqual(constants.address2EditDis);
        expect(cannon.getText()).toEqual(constants.address2EditCan);
        browser.sleep(500);
    });

    it('should be able to create a new Address2 through the vif:', function(){
        browser.get(constants.webAddress + '/data-entry/vifs/create/');
        browser.sleep(500);
        this.victim_address_address2 = element(by.id("id_victim_address_address2")).click();
        browser.sleep(500);
        address2AdminPage.createNewAddress2();
        browser.sleep(500);
        address2AdminPage.navigate();

        browser.sleep(1000);

        expect(element(by.xpath("//td[text() = '" + constants.address2NewName + "']")).isPresent()).toBe(true);
        var item = element(by.xpath("//td[text() = '" + constants.address2NewName + "']"));
        var address1 = item.element(by.xpath("../td[4]"));
        var cannon = item.element(by.xpath("../td[5]"));

        expect(address1.getText()).toEqual(constants.address2NewDis);
        expect(cannon.getText()).toEqual(constants.address2NewCan);
    });

    it('should be able to be paginated by a different number', function () {
        element(by.cssContainingText('option', '50')).click();
        expect(element(by.model('vm.paginateBy')).isPresent()).toBe(true);
    });

    it('should be able to search', function () {
        element(by.model('vm.searchValue')).clear().sendKeys("Sudap").then(function (){
            element(by.linkText('Search')).click();
        }).then(function () {
            browser.sleep(500);
            expect(element.all(by.className('address-name')).first().getText()).toBe("Sudap");
        });
    });

    it('should be able to be filtered by the address name', function () {
        var firstElement = element.all(by.className("address-name")).first().getText().then(function () {
            element(by.id("addressNameHeader")).click();
            browser.sleep(500);
            var lastAddress = element.all(by.className("address-name")).first();
            browser.sleep(1000);
            expect(lastAddress.getText()).not.toEqual(firstElement); // We know our new address name will be on top
        });
    });

});
