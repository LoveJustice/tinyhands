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
        this.editVdcName = element(by.id("id_name")).clear().sendKeys(c.vdcNewName);
        this.editVdcDistrict = element(by.cssContainingText('option', 'Achham')).click();
        this.editVdccannonical = element(by.cssContainingText('option', 'Chalsa')).click();
        browser.sleep(500);
        this.editVdcSubmit = element(by.id("vdc_update_button")).click();
        browser.sleep(500);
    };

    //
    //changeValues
    //this.checkIfVdcUpdated = function(){
    //
    //
    //};

};

module.exports = new vdcAdminPage();