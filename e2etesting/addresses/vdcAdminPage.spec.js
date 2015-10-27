var constants = require('../testConstants.json');
var loginPage = require('../accounts/loginPage.js');
var vdcAdminPage = require('./vdcAdminPage.js');

describe('TinyHands VDCs', function () {
    beforeEach(function () {
        return browser.ignoreSynchronization = true;
    });

    it('should navigate to VDC manage page', function () {
        loginPage.logout();
        loginPage.loginAsAdmin();
        vdcAdminPage.navigate();
        expect(browser.getTitle()).toContain('Manage');
    });

    it('should change the first VDCs information', function () {
        browser.ignoreSynchronization = false;
        browser.sleep(500);

        //browser.pause();

        element.all(by.className("edit")).first().click();
        browser.sleep(500);
        //browser.ignoreSynchronization = false;
        vdcAdminPage.changeValues();
        browser.ignoreSynchronization = true;
        browser.sleep(1000);
        browser.get(constants.webAddress);
        vdcAdminPage.navigate();


        browser.sleep(1000);
        var item = element(by.xpath("//td[text() = '" + constants.vdcEditName + "']"));
        var district = item.element(by.xpath("../td[4]"));
        var cannon = item.element(by.xpath("../td[5]"));

        expect(item.getText()).toEqual(constants.vdcEditName);
        expect(district.getText()).toEqual(constants.vdcEditDis);
        expect(cannon.getText()).toEqual(constants.vdcEditCan);
        browser.sleep(500);
    });

    it('should be able to create a new VDC through the vif:', function(){
        browser.get(constants.webAddress + '/data-entry/vifs/create/');
        browser.sleep(500);
        this.victim_address_vdc = element(by.id("id_victim_address_vdc")).click();
        browser.sleep(500);
        vdcAdminPage.createNewVDC();
        browser.sleep(500);
        vdcAdminPage.navigate();

        browser.sleep(1000);

        expect(element(by.xpath("//td[text() = '" + constants.vdcNewName + "']")).isPresent()).toBe(true);
        var item = element(by.xpath("//td[text() = '" + constants.vdcNewName + "']"));
        var district = item.element(by.xpath("../td[4]"));
        var cannon = item.element(by.xpath("../td[5]"));

        expect(district.getText()).toEqual(constants.vdcNewDis);
        expect(cannon.getText()).toEqual(constants.vdcNewCan);
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
