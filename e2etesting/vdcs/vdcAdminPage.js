'use strict';

var constants = require('../testConstants.json');

var vdcAdminPage = function () {
    var page = this;

    this.navigate = function () {
        browser.get('http://0.0.0.0:8000/data-entry/geocodelocations/vdc-admin/');
        this.findItemsOnPage();
    };

   this.findItemsOnPage = function () {
        this.firstVdcName = element(by.css(".vdc_admin_name"));
        this.firstVdcLatitude = element.all(by.css(".vdc_admin_latitude")).first().getText();
        this.firstVdclongitude = element.all(by.css(".vdc_admin_longitude")).first().getText();
        this.firstVdcDistrict = element.all(by.css(".vdc_admin_district")).first().getText();
        this.firstVdccannonical = element.all(by.css(".vdc_admin_cannonical")).first().getText();
        this.firstVdcVerified = element.all(by.css(".vdc_admin_verified")).first().getText();
        this.firstVdcEditButton = element.all(by.id("vdc_update_link")).first();
    };

    this.checkIfValuesAreEqual = function () {
        this.editVdcName = element(by.id("id_name"));
        this.editVdcLatitude = element(by.id("id_latitude")).first().getText();
        this.editVdclongitude = element(by.id("id_longitude")).first().getText();
        this.editVdcDistrict = element(by.id("id_district")).first().getText();
        this.editVdccannonical = element(by.id("id_cannonical_name")).first().getText();
        this.editVdcVerified = element(by.id("id_verified")).first().getText();
        this.editVdcSubmit = element(by.css("btn btn-primary")).first();
    };
    //
    //changeValues
    //this.checkIfVdcUpdated = function(){
    //
    //
    //};

};

module.exports = new vdcAdminPage();