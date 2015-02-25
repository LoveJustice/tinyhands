'use strict';

var c = require('../testConstants.json');

var vdcAdminPage = function () {
    var page = this;

    this.navigate = function () {
        browser.get(c.webAddress + '/data-entry/geocodelocations/vdc-admin/');
        this.findItemsOnPage();
    };

   this.findItemsOnPage = function () {
        this.firstVdcName = element(by.css(".vdc_admin_name")).getText();
        this.firstVdcDistrict = element.all(by.css(".vdc_admin_district")).get(3).getText();
        this.firstVdccannonical = element.all(by.css(".vdc_admin_cannonical")).get(3).getText();
        this.firstVdcVerified = element.all(by.css(".vdc_admin_verified")).get(3).getText();
        this.firstVdcEditButton = element.all(by.id("vdc_update_link")).get(3);
    };


    this.changeValues = function () {
        this.editVdcName = element(by.id("id_name")).clear().sendKeys(c.vdcEditName);
        this.editVdcDistrict = element(by.cssContainingText('option', c.vdcEditDis)).click();
        this.editVdccannonical = element(by.cssContainingText('option', c.vdcEditCan)).click();
        this.editVdcSubmit = element(by.id("vdc_update_button")).click();
    };

    this.createNewVDC = function() {
        this.vdcCreateButton = element(by.id("vdc_create_page")).click();
        browser.sleep(500);
        this.newVdcName = element(by.id("id_name")).clear().sendKeys(c.vdcNewName);
        this.newVdcLatitude = element(by.id("id_latitude")).clear().sendKeys(c.vdcNewLat);
        this.newVdcLongitude = element(by.id("id_longitude")).clear().sendKeys(c.vdcNewLon);
        this.editVdcDistrict = element(by.cssContainingText('option', c.vdcNewDis)).click();
        this.editVdccannonical = element(by.cssContainingText('option', c.vdcNewCan)).click().submit();
    };


};

module.exports = new vdcAdminPage();