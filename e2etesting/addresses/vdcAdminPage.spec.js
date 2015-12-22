var constants = require('../testConstants.json');
var loginPage = require('../accounts/loginPage.js');
var vdcAdminPage = require('./vdcAdminPage.js');

describe('TinyHands VDCs', function () {
    beforeEach(function () {
        return browser.ignoreSynchronization = true;
        //browser.manage().timeouts().implicitlyWait(5000);
    });

    it('should navigate to VDC manage page', function () {
        loginPage.logout();
        loginPage.loginAsAdmin();
        vdcAdminPage.navigate();
        expect(browser.getTitle()).toContain('Manage');
    });

    it('should change the first VDCs information', function () {
        browser.ignoreSynchronization = false;

        element.all(by.className("edit")).first().click();
        vdcAdminPage.changeValues();
        browser.ignoreSynchronization = true;
        browser.get(constants.webAddress);
        vdcAdminPage.navigate();

        browser.wait(function(){
            return element(by.xpath("//td[text() = '" + constants.vdcEditName + "']")).isPresent();
        }, 12000).then(function(){
            var item = element(by.xpath("//td[text() = '" + constants.vdcEditName + "']"));
            var district = item.element(by.xpath("../td[4]"));
            var cannon = item.element(by.xpath("../td[5]"));

            expect(item.getText()).toEqual(constants.vdcEditName);
            expect(district.getText()).toEqual(constants.vdcEditDis);
            expect(cannon.getText()).toEqual(constants.vdcEditCan);
        });
    });

    it('should be able to create a new VDC through the vif:', function(){
        browser.get(constants.webAddress + '/data-entry/vifs/create/');
        this.victim_address_vdc = element(by.id("id_victim_address_vdc")).click();
        vdcAdminPage.createNewVDC();
        vdcAdminPage.navigate();

        browser.wait(protractor.ExpectedConditions.presenceOf(element(by.xpath("//td[text() = '" + constants.vdcNewName + "']"))), 5000);

        expect(element(by.xpath("//td[text() = '" + constants.vdcNewName + "']")).isPresent()).toBe(true);
        var item = element(by.xpath("//td[text() = '" + constants.vdcNewName + "']"));
        var district = item.element(by.xpath("../td[4]"));
        var cannon = item.element(by.xpath("../td[5]"));

        expect(district.getText()).toEqual(constants.vdcNewDis);
        expect(cannon.getText()).toEqual(constants.vdcNewCan);

    });

    it('should be able to be paginated by a different number', function () {
        browser.ignoreSynchronization = false;

        element(by.cssContainingText('option', '50')).click();
        expect(element(by.model('vm.paginateBy')).isPresent()).toBe(true);
    });

    it('should be able to search', function () {
        browser.ignoreSynchronization = false;
        element(by.model('vm.searchValue')).clear().sendKeys("Sudap").then(function (){
            element(by.linkText('Search')).click();
        });

        browser.wait(function(){
            return element.all(by.className('address-name')).first().isPresent();

        }, 10000).then(function(){
           expect(element.all(by.className('address-name')).first().getText()).toBe("Sudap");
        });
    });

    it('should be able to be filtered by the address name', function () {
        browser.ignoreSynchronization = false;
        //Do a refresh in order to clear the search state.
        browser.refresh();

        browser.wait(function(){
            return element.all(by.className("address-name")).first().isPresent();
        }, 10000).then(function(){
            var firstElement = element.all(by.className("address-name")).first().getText();
            element(by.id("addressNameHeader")).click();

            browser.wait(function(){
                return element.all(by.className("address-name")).first().isPresent();
            }, 10000).then(function(){
                var lastAddress = element.all(by.className("address-name")).first();
                expect(lastAddress.getText()).not.toEqual(firstElement); // We know our new address name will be on top
            });
        });

    });

});
