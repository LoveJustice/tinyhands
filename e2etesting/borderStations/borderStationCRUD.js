'use strict';

var c = require('../testConstants.json');

var borderStationPage = function() {
    var page = this;

    this.getToBoarderStationCreate = function(){
        browser.get(c.webAddress + '/static_border_stations/border-stations/create/');
        };

    this.fillOutBoarderStation = function() {
        this.station_name = element(by.id("id_station_name")).sendKeys(c.stationName);
        this.station_code = element(by.id("id_station_code")).sendKeys(c.stationCode);
        this.date_established = element(by.id("id_date_established")).sendKeys(c.dateEstablished);
        this.has_shelter = element(by.id("id_has_shelter")).click();
        this.latitude = element(by.id("id_latitude")).sendKeys(c.latitude);
        this.longitude = element(by.id("id_longitude")).sendKeys(c.longitude);
        this.staff0_first_name = element(by.id("id_staff_set-0-first_name")).sendKeys(c.staff0SetFirstName);
        this.staff0_last_name = element(by.id("id_staff_set-0-last_name")).sendKeys(c.staff0SetLastName);
        this.staff0_email = element(by.id("id_staff_set-0-email")).sendKeys(c.staff0Email);
        this.staff0_receives_money_distribution_form = element(by.id("id_staff_set-0-receives_money_distribution_form")).click();

        this.committee0_first_name = element(by.id("id_committeemember_set-0-first_name")).sendKeys(c.committee0SetFirstName);
        this.committee0_last_name = element(by.id("id_committeemember_set-0-last_name")).sendKeys(c.committee0SetLastName);
        this.committee0_email = element(by.id("id_committeemember_set-0-email")).sendKeys(c.committee0Email);
        this.committee0_receives_money_distribution_form = element(by.id("id_committeemember_set-0-receives_money_distribution_form")).click();

        /*
        this.committee0_first_name = element(by.id("id_location_set-0-name")).sendKeys(c.committee0SetFirstName);
        this.committee0_last_name = element(by.id("id_committeemember_set-0-last_name")).sendKeys(c.committee0SetLastName);
        this.committee0_email = element(by.id("id_committeemember_set-0-email")).sendKeys(c.committee0Email);
        this.committee0_receives_money_distribution_form = element(by.id("id_staff_set-0-receives_money_distribution_form")).click();
        */
        /*
        this.dIRF = element(by.linkText('+ Add Another Staff')).click();
        this.staff1_first_name = element(by.id("id_staff_set-1-first_name")).sendKeys(c.staff1SetFirstName);
        this.staff1_last_name = element(by.id("id_staff_set-1-last_name")).sendKeys(c.staff1SetLastName);
        this.staff1_email = element(by.id("id_staff_set-1-email")).sendKeys(c.staff1Email);
        this.staff1_receives_money_distribution_form = element(by.id("id_staff_set-1-receives_money_distribution_form")).click();
        */

    };

};

module.exports = new borderStationPage();