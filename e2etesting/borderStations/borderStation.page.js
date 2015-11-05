'use strict';

var c = require('../testConstants.json');
var methods = require('../commonMethods.js');

var borderStationPage = function() {
    var page = this; // So if we have any things that create a new scope, we can always reference page without this problems

    page.station_name = element(by.id("id_station_name"));
    page.station_code = element(by.id("id_station_code"));
    page.date_established = element(by.id("id_date_established"));
    page.has_shelter = element(by.id("id_has_shelter"));
    page.latitude = element(by.id("id_latitude"));
    page.longitude = element(by.id("id_longitude"));
    page.stationClosedButton = element(by.css(".openclosed"));
    page.stationClosedButtonLabel = element(by.css('.openclosedlabel'));

    page.staff0_first_name = element(by.id("id_staff_set-0-first_name"));
    page.staff0_last_name = element(by.id("id_staff_set-0-last_name"));
    page.staff0_email = element(by.id("id_staff_set-0-email"));
    page.staff0_receives_money_distribution_form = element(by.id("id_staff_set-0-receives_money_distribution_form"));
    page.staff1_first_name = element(by.id("id_staff_set-1-first_name"));
    page.staff1_last_name = element(by.id("id_staff_set-1-last_name"));
    page.staff1_email = element(by.id("id_staff_set-1-email"));
    page.staff1_receives_money_distribution_form = element(by.id("id_staff_set-1-receives_money_distribution_form"));
    page.staff2_first_name = element(by.id("id_staff_set-2-first_name"));
    page.staff2_last_name = element(by.id("id_staff_set-2-last_name"));
    page.staff2_receives_money_distribution_form = element(by.id("id_staff_set-2-receives_money_distribution_form"));

    page.committee0_first_name = element(by.id("id_committeemember_set-0-first_name"));
    page.committee0_last_name = element(by.id("id_committeemember_set-0-last_name"));
    page.committee0_email = element(by.id("id_committeemember_set-0-email"));
    page.committee0_receives_money_distribution_form = element(by.id("id_committeemember_set-0-receives_money_distribution_form"));
    page.committee1_first_name = element(by.id("id_committeemember_set-1-first_name"));
    page.committee1_last_name = element(by.id("id_committeemember_set-1-last_name"));
    page.committee1_email = element(by.id("id_committeemember_set-1-email"));
    page.committee1_receives_money_distribution_form = element(by.id("id_committeemember_set-1-receives_money_distribution_form"));
    page.committee2_first_name = element(by.id("id_committeemember_set-2-first_name"));
    page.committee2_last_name = element(by.id("id_committeemember_set-2-last_name"));
    page.committee2_receives_money_distribution_form = element(by.id("id_committeemember_set-2-receives_money_distribution_form"));

    page.location0_set_name = element(by.id("id_location_set-0-name"));
    page.location0_set_latitude = element(by.id("id_location_set-0-latitude"));
    page.location0_set_longitude = element(by.id("id_location_set-0-longitude"));
    page.location1_set_name = element(by.id("id_location_set-1-name"));
    page.location1_set_latitude = element(by.id("id_location_set-1-latitude"));
    page.location1_set_longitude = element(by.id("id_location_set-1-longitude"));
    page.location2_set_name = element(by.id("id_location_set-2-name"));
    page.location2_set_latitude = element(by.id("id_location_set-2-latitude"));
    page.location2_set_longitude = element(by.id("id_location_set-2-longitude"));

    page.border_station_update_button = element(by.id("borderUpdate"));


    page.getToBorderStationCreate = function(){
        browser.get(c.webAddress + '/portal/dashboard/');
        browser.sleep(200);
        element(by.id("border_station_dropdown")).click();
        browser.sleep(200);
        element(by.id("border_station_create_link")).click();
        browser.sleep(200);
    };

    page.fillOutBorderStation = function(stationName, stationCode) {
        var stationName = stationName ? stationName : c.stationName;
        var stationCode = stationCode ? stationCode : c.stationCode;

        page.station_name.sendKeys(stationName);
        page.station_code.sendKeys(stationCode);
        page.date_established.sendKeys(c.dateEstablished);
        page.has_shelter.click();
        page.latitude.sendKeys(c.latitude);
        page.longitude.sendKeys(c.longitude);

        page.staff0_first_name.sendKeys(c.staff0SetFirstName);
        page.staff0_last_name.sendKeys(c.staff0SetLastName);
        page.staff0_email.sendKeys(c.staff0Email);
        page.staff0_receives_money_distribution_form.click();

        page.committee0_first_name.sendKeys(c.committee0SetFirstName);
        page.committee0_last_name.sendKeys(c.committee0SetLastName);
        page.committee0_email.sendKeys(c.committee0Email);
        page.committee0_receives_money_distribution_form.click();

        page.location0_set_name.sendKeys(c.location0SetName);
        page.location0_set_latitude.sendKeys(c.location0SetLatitude);
        browser.sleep(500);
        page.location0_set_longitude.sendKeys(c.location0SetLongitude).submit();
        browser.sleep(500);
    };

    page.fillOutBorderStationWithNoEmail = function() {
        page.station_name.sendKeys(c.stationName);
        page.station_code.sendKeys(c.stationCode);
        page.date_established.sendKeys(c.dateEstablished);
        page.has_shelter.click();
        page.latitude.sendKeys(c.latitude);
        page.longitude.sendKeys(c.longitude);

        page.staff0_first_name.sendKeys(c.staff0SetFirstName);
        page.staff0_last_name.sendKeys(c.staff0SetLastName);
        page.staff0_receives_money_distribution_form.click();

        page.committee0_first_name.sendKeys(c.committee0SetFirstName);
        page.committee0_last_name.sendKeys(c.committee0SetLastName);
        page.committee0_receives_money_distribution_form.click();

        page.location0_set_name.sendKeys(c.location0SetName);
        page.location0_set_latitude.sendKeys(c.location0SetLatitude);
        page.location0_set_longitude.sendKeys(c.location0SetLongitude).submit();

    };

    page.viewBorderStation = function() {
        browser.get(c.webAddress + '/static_border_stations/border-stations/update/' + c.stationId + '/');
    };

    page.closeBorderStation = function() {
        page.border_station_update_button.click();
    };

    page.editBorderStation = function() {
        browser.get(c.webAddress + '/static_border_stations/border-stations/update/' + c.stationId + '/');

        page.staff1_first_name.sendKeys(c.staff1SetFirstName);
        page.staff1_last_name.sendKeys(c.staff1SetLastName);
        page.staff1_email.sendKeys(c.staff1Email);
        page.staff1_receives_money_distribution_form.click();

        page.committee1_first_name.sendKeys(c.committee1SetFirstName);
        page.committee1_last_name.sendKeys(c.committee1SetLastName);
        page.committee1_email.sendKeys(c.committee1Email);
        page.committee1_receives_money_distribution_form.click();

        page.location1_set_name.sendKeys(c.location1SetName);
        page.location1_set_latitude.sendKeys(c.location1SetLatitude);
        page.location1_set_longitude.sendKeys(c.location1SetLongitude);

        page.border_station_update_button.click();
    };

    page.editBorderStationWithNoEmail = function() {
        return browser.get(c.webAddress + '/static_border_stations/border-stations/update/' + c.stationId + '/')
            .then(function() {
                page.staff2_first_name.sendKeys(c.staff1SetFirstName);
                page.staff2_last_name.sendKeys(c.staff1SetLastName);
                page.staff2_receives_money_distribution_form.click();

                page.committee2_first_name.sendKeys(c.committee1SetFirstName);
                page.committee2_last_name.sendKeys(c.committee1SetLastName);
                page.committee2_receives_money_distribution_form.click();

                page.location2_set_name.sendKeys(c.location1SetName);
                page.location2_set_latitude.sendKeys(c.location1SetLatitude);
                page.location2_set_longitude.sendKeys(c.location1SetLongitude);

                page.border_station_update_button.click();
            });
    };
};

module.exports = borderStationPage;
