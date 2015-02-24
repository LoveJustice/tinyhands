'use strict';

var c = require('../testConstants.json');

var vdcAdminPage = function () {
    var page = this;

    this.navigate = function () {
        browser.get('http://0.0.0.0:8000/data-entry/geocodelocations/vdc-admin/');
        this.findItemsOnPage();
    };

   this.findItemsOnPage = function () {
        this.firstVdcName = element(by.css(".vdc_admin_name")).getText();
        this.firstVdcLatitude = element.all(by.css(".vdc_admin_latitude")).first().getText();
        this.firstVdclongitude = element.all(by.css(".vdc_admin_longitude")).first().getText();
        this.firstVdcDistrict = element.all(by.css(".vdc_admin_district")).first().getText();
        this.firstVdccannonical = element.all(by.css(".vdc_admin_cannonical")).first().getText();
        this.firstVdcVerified = element.all(by.css(".vdc_admin_verified")).first().getText();
        this.firstVdcEditButton = element.all(by.id("vdc_update_link")).first();
    };


    this.changeValues = function () {
        this.editVdcName = element(by.id("id_name")).clear().sendKeys(c.vdcNewName);
        this.editVdcLatitude = element(by.id("id_latitude")).clear().sendKeys(c.vdcNewLat);
        this.editVdclongitude = element(by.id("id_longitude")).clear().sendKeys(c.vdcNewLon);
        this.editVdcDistrict = element(by.cssContainingText('option', 'Achham')).click();
        this.editVdccannonical = element(by.cssContainingText('option', 'Chalsa')).click();
        this.editVdcSubmit = element(by.id("vdc_update_button")).click();
    };

    //
    //changeValues
    //this.checkIfVdcUpdated = function(){
    //
    //
    //};

};

module.exports = new vdcAdminPage();