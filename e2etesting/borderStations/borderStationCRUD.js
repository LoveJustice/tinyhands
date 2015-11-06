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

    this.fillOutBorderStation = function() {


        browser.driver.wait(function() {
            return browser.driver.findElement(by.id('stationName')).then(function(elem) {
                    return true;
                });
        }, 20000);

        browser.sleep(3000);

        //browser.pause();

        this.station_name = element(by.id("stationName")).sendKeys(c.stationName);
        this.station_code = element(by.id("stationCode")).sendKeys(c.stationCode);
        this.date_established = element(by.id("dateEstablished")).sendKeys(c.dateEstablished);
        this.has_shelter = element(by.id("hasShelter")).click();
        this.latitude = element(by.id("latitude")).sendKeys(c.latitude);
        this.longitude = element(by.id("longitude")).sendKeys(c.longitude);

        this.staff0_first_name = element(by.id("S-firstName-0")).sendKeys(c.staff0SetFirstName);
        this.staff0_last_name = element(by.id("S-lastName-0")).sendKeys(c.staff0SetLastName);
        this.staff0_email = element(by.id("S-email-0")).sendKeys(c.staff0Email);
        this.staff0_receives_money_distribution_form = element(by.id("S-receivesMoneyDistributionForm-0")).click();

        this.committee0_first_name = element(by.id("C-firstName-0")).sendKeys(c.committee0SetFirstName);
        this.committee0_last_name = element(by.id("C-lastName-0")).sendKeys(c.committee0SetLastName);
        this.committee0_email = element(by.id("C-email-0")).sendKeys(c.committee0Email);
        this.committee0_receives_money_distribution_form = element(by.id("C-receivesMoneyDistributionForm-0")).click();

        this.location0_set_name = element(by.id("locationName-0")).sendKeys(c.location0SetName);
        this.location0_set_latitude = element(by.id("latitude-0")).sendKeys(c.location0SetLatitude);
        browser.sleep(500);
        this.location0_set_longitude = element(by.id("longitude-0")).sendKeys(c.location0SetLongitude).submit();
        browser.sleep(500);
    };

    this.fillOutBorderStationWithNoEmail = function() {
        this.station_name = element(by.id("stationName")).sendKeys(c.stationName);
        this.station_code = element(by.id("stationCode")).sendKeys(c.stationCode);
        this.date_established = element(by.id("dateEstablished")).sendKeys(c.dateEstablished);
        this.has_shelter = element(by.id("hasShelter")).click();
        this.latitude = element(by.id("latitude")).sendKeys(c.latitude);
        this.longitude = element(by.id("longitude")).sendKeys(c.longitude);

        this.staff0_first_name = element(by.id("S-firstName-0")).sendKeys(c.staff0SetFirstName);
        this.staff0_last_name = element(by.id("S-lastName-0")).sendKeys(c.staff0SetLastName);
        this.staff0_receives_money_distribution_form = element(by.id("S-receivesMoneyDistributionForm-0")).click();

        this.committee0_first_name = element(by.id("C-firstName-0")).sendKeys(c.committee0SetFirstName);
        this.committee0_last_name = element(by.id("C-lastName-0")).sendKeys(c.committee0SetLastName);
        this.committee0_receives_money_distribution_form = element(by.id("C-receivesMoneyDistributionForm-0")).click();

        this.location0_set_name = element(by.id("locationName-0")).sendKeys(c.location0SetName);
        this.location0_set_latitude = element(by.id("latitude-0")).sendKeys(c.location0SetLatitude);
        this.location0_set_longitude = element(by.id("longitude-0")).sendKeys(c.location0SetLongitude).submit();

    }

    this.viewBorderStation = function() {
        browser.get(c.webAddress + '/static_border_stations/border-stations/update/' + c.stationId + '/');
    };

    this.closeBorderStation = function() {
        methods.click(element(by.id("borderUpdate")));
        //this.closeBorder =  element(by.id("borderUpdate")).click()
    };

    this.editBorderStation = function() {
        browser.get(c.webAddress + '/static_border_stations/border-stations/update/' + c.stationId + '/');

        //this.dIRF = element(by.linkText('+ Add Another Staff')).click();
        this.staff1_first_name = element(by.id("id_staff_set-1-first_name")).sendKeys(c.staff1SetFirstName);
        this.staff1_last_name = element(by.id("id_staff_set-1-last_name")).sendKeys(c.staff1SetLastName);
        this.staff1_email = element(by.id("id_staff_set-1-email")).sendKeys(c.staff1Email);
        this.staff1_receives_money_distribution_form = element(by.id("id_staff_set-1-receives_money_distribution_form")).click();

        this.committee1_first_name = element(by.id("id_committeemember_set-1-first_name")).sendKeys(c.committee1SetFirstName);
        this.committee1_last_name = element(by.id("id_committeemember_set-1-last_name")).sendKeys(c.committee1SetLastName);
        this.committee1_email = element(by.id("id_committeemember_set-1-email")).sendKeys(c.committee1Email);
        this.committee1_receives_money_distribution_form = element(by.id("id_committeemember_set-1-receives_money_distribution_form")).click();

        this.location1_set_name = element(by.id("id_location_set-1-name")).sendKeys(c.location1SetName);
        this.location1_set_latitude = element(by.id("id_location_set-1-latitude")).sendKeys(c.location1SetLatitude);
        this.location1_set_longitude = element(by.id("id_location_set-1-longitude")).sendKeys(c.location1SetLongitude);

        methods.click(element(by.id("borderUpdate")));
        //this.updateBorder = element(by.id("borderUpdate")).click();
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
