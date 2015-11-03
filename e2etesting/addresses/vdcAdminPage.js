var c = require('../testConstants.json');

var vdcAdminPage = function () {
    var page = this;

    this.navigate = function () {
        browser.get(c.webAddress + '/data-entry/geocodelocations/vdc-admin/');
    };

    this.changeValues = function () {
        this.editVdcName = element(by.id('addressName')).clear().sendKeys(c.vdcEditName);
        browser.sleep(300);
        this.editVdcDistrict = element(by.id('address1')).click().clear().sendKeys(c.vdcEditDis);
        browser.sleep(500);
        this.exactItem = element(by.repeater("match in matches").row(0)).click();
        browser.actions().sendKeys(protractor.Key.ENTER).perform();
        browser.sleep(300);
        this.editVdccannonical = element(by.id('canonical_name')).click().clear().sendKeys(c.vdcEditCan);
        this.exactItem2 = element(by.repeater("match in matches").row(0)).click()
        //browser.actions().sendKeys(protractor.Key.ENTER).perform();
        browser.sleep(200);

        this.editVdcSubmit = element(by.buttonText('Save')).click();

        browser.sleep(1000);
    };

    this.createNewVDC = function() {
        browser.sleep(1000);
        this.vdcCreateButton = element(by.id("vdc_create_page")).click();
        browser.sleep(500);
        this.newVdcName = element(by.id("id_name")).clear().sendKeys(c.vdcNewName);
        this.newVdcLatitude = element(by.id("id_latitude")).clear().sendKeys(c.vdcNewLat);
        this.newVdcLongitude = element(by.id("id_longitude")).clear().sendKeys(c.vdcNewLon);
        this.editVdcDistrict = element(by.cssContainingText('option', c.vdcNewDis)).click();
        this.editVdccannonical = element(by.cssContainingText('option', c.vdcNewCan)).click();
        this.editVdccannonical = element(by.cssContainingText('option', c.vdcNewCan)).submit();
        browser.sleep(500);
    };


};

module.exports = new vdcAdminPage();
