var c = require('../testConstants.json');

var address2AdminPage = function () {
    var page = this;

    this.navigate = function () {
        browser.get(c.webAddress + '/data-entry/geocodelocations/address2-admin/');
    };

    this.changeValues = function () {
        this.editAddress2Name = element(by.id('addressName')).clear().sendKeys(c.address2EditName);
        browser.sleep(300);
        this.editAddress2Address1 = element(by.id('address1')).click().clear().sendKeys(c.address2EditDis);
        browser.sleep(500);
        this.exactItem = element(by.repeater("match in matches").row(0)).click();
        browser.actions().sendKeys(protractor.Key.ENTER).perform();
        browser.sleep(300);
        this.editAddress2canonical = element(by.id('canonical_name')).click().clear().sendKeys(c.address2EditCan);
        this.exactItem2 = element(by.repeater("match in matches").row(0)).click()
        //browser.actions().sendKeys(protractor.Key.ENTER).perform();
        browser.sleep(200);

        this.editAddress2Submit = element(by.buttonText('Save')).click();

        browser.sleep(1000);
    };

    this.createNewAddress2 = function() {
        browser.sleep(1000);
        this.address2CreateButton = element(by.id("address2_create_page")).click();
        browser.sleep(500);
        this.newAddress2Name = element(by.id("id_name")).clear().sendKeys(c.address2NewName);
        this.newAddress2Latitude = element(by.id("id_latitude")).clear().sendKeys(c.address2NewLat);
        this.newAddress2Longitude = element(by.id("id_longitude")).clear().sendKeys(c.address2NewLon);
        this.editAddress2Address1 = element(by.cssContainingText('option', c.address2NewDis)).click();
        this.editAddress2canonical = element(by.cssContainingText('option', c.address2NewCan)).click();
        this.editAddress2canonical = element(by.cssContainingText('option', c.address2NewCan)).submit();
        browser.sleep(500);
    };


};

module.exports = new address2AdminPage();
