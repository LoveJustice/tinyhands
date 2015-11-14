'use strict';

var c = require('../testConstants.json');
var methods = require('../commonMethods.js');

var borderStationPage = function() {
    var page = this;

    this.getToBorderStationCreate = function(){
        browser.get(c.webAddress + '/portal/dashboard/');

        browser.driver.wait(function() {
            return browser.driver.findElement(by.id('border_station_dropdown')).then(function(elem) {
                    elem.click();
                    return true;
                });
        }, 20000);

        browser.driver.wait(function() {
            return browser.driver.findElement(by.id('border_station_create_link')).then(function(elem) {
                    elem.click();
                    return true;
                });
        }, 20000);
    };

    this.fillOutBorderStation = function(stationName, stationCode) {
        this.station_name = element(by.id("stationName")).sendKeys(stationName);
        this.station_code = element(by.id("stationCode")).sendKeys(stationCode);
        this.date_established = element(by.id("dateEstablished")).sendKeys(c.dateEstablished);
        this.has_shelter = element(by.id("hasShelter")).click();
        this.latitude = element(by.id("latitude")).sendKeys(c.latitude);
        this.longitude = element(by.id("longitude")).sendKeys(c.longitude);
        this.submit = element(by.css('[ng-click="bsCtrl.modifyStation()"]')).click();
    };

    this.addBorderStationStaff = function() {

        this.editBorderStation();

        this.add = element(by.xpath("//button[text()='Add Staff']")).click();
        this.staff0_first_name = element(by.id("S-firstName-0")).sendKeys(c.staff0SetFirstName);
        this.staff0_last_name = element(by.id("S-lastName-0")).sendKeys(c.staff0SetLastName);
        this.staff0_email = element(by.id("S-email-0")).sendKeys(c.staff0Email);
        this.staff0_phone = element(by.id("S-phone-0")).sendKeys(c.staff0Phone);
        this.staff0_position = element(by.id("S-position-0")).sendKeys(c.staff0Position);
        this.MDF_checkbox = element(by.id("S-receivesMoneyDistributionForm-0")).click();
        this.saveForm();
    };

    this.addBorderStationCommitteeMember = function() {

        this.editBorderStation();

        this.add = element(by.xpath("//button[text()='Add Committee Members']")).click();
        this.committee0_first_name = element(by.id("C-firstName-0")).sendKeys(c.staff0SetFirstName);
        this.committee0_last_name = element(by.id("C-lastName-0")).sendKeys(c.staff0SetLastName);
        this.committee0_email = element(by.id("C-email-0")).sendKeys(c.staff0Email);
        this.committee0_phone = element(by.id("C-phone-0")).sendKeys(c.staff0Phone);
        this.committee0_position = element(by.id("C-position-0")).sendKeys(c.staff0Position);
        this.saveForm();
    };

    this.addBorderStationLocation = function() {
        this.editBorderStation();
        this.add = element(by.xpath("//button[text()='Add Location']")).click();
        this.location = element(by.id("locationName-0")).sendKeys(c.location0SetName);
        this.latitude = element(by.id("latitude-0")).sendKeys(c.location0SetLatitude);
        this.longitude = element(by.id("longitude-0")).sendKeys(c.location0SetLongitude);

        this.saveForm();
    };


    this.saveForm = function() {
        this.submit = element(by.css('[ng-click="bsCtrl.modifyStation()"]')).click();
    };

    this.fillOutBorderStationWithNoEmail = function() {
        this.station_name = element(by.id("stationName")).sendKeys(c.stationName);
        this.station_code = element(by.id("stationCode")).sendKeys(c.stationCode);
        this.date_established = element(by.id("dateEstablished")).sendKeys(c.dateEstablished);
        this.has_shelter = element(by.id("hasShelter")).click();
        this.latitude = element(by.id("latitude")).sendKeys(c.latitude);
        this.longitude = element(by.id("longitude")).sendKeys(c.longitude);
        this.submit = element(by.css('[ng-click="bsCtrl.modifyStation()"]')).click();
    };

    this.viewBorderStation = function() {
        browser.get(c.webAddress + '/static_border_stations/border-stations/update/' + c.stationId + '/');
    };

    this.closeBorderStation = function() {
        methods.click(element(by.id("borderUpdate")));
        //this.closeBorder =  element(by.id("borderUpdate")).click()
    };

    this.editBorderStation = function() {
        browser.get(c.webAddress + '/static_border_stations/border-stations/update/' + c.stationId + '/');
    };

    this.editBorderStationWithNoEmail = function() {
        return browser.get(c.webAddress + '/static_border_stations/border-stations/update/' + c.stationId + '/')
            .then(function() {
                element(by.id("id_staff_set-2-first_name")).sendKeys(c.staff1SetFirstName);
                element(by.id("id_staff_set-2-last_name")).sendKeys(c.staff1SetLastName);
                element(by.id("id_staff_set-2-receives_money_distribution_form")).click();

                element(by.id("id_committeemember_set-2-first_name")).sendKeys(c.committee1SetFirstName);
                element(by.id("id_committeemember_set-2-last_name")).sendKeys(c.committee1SetLastName);
                element(by.id("id_committeemember_set-2-receives_money_distribution_form")).click();

                element(by.id("id_location_set-2-name")).sendKeys(c.location1SetName);
                element(by.id("id_location_set-2-latitude")).sendKeys(c.location1SetLatitude);
                element(by.id("id_location_set-2-longitude")).sendKeys(c.location1SetLongitude);

                element(by.id("borderUpdate")).click();
            });
    };
};

module.exports = new borderStationPage();