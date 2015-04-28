var c = require('../testConstants.json');
var loginPage = require('../accounts/loginPage.js');
var borderStationPage = require('./borderStationCRUD.js');

describe('Border Station CRUD', function() {

    beforeEach(function () {
        return browser.ignoreSynchronization = true;
    });

    describe('Border Station CRUD TESTS', function () {
        it('accepts credentials', function () {
            loginPage.logout();
            loginPage.loginAsAdmin();
        });

        it('Create Border Station', function () {
            borderStationPage.getToBorderStationCreate();
            expect(browser.driver.getCurrentUrl()).toContain('/static_border_stations/border-stations/create/');
            borderStationPage.fillOutBorderStation();
            expect(browser.driver.getCurrentUrl()).toContain('/portal/dashboard/');
        });


        it('View Border Station', function () {
            borderStationPage.viewBorderStation();
            expect(browser.driver.getCurrentUrl()).toContain('/static_border_stations/border-stations/update/24/');
            expect(element(by.id("id_station_name")).getAttribute('value')).toEqual(c.stationName);

            expect(element(by.id("id_station_code")).getAttribute('value')).toEqual(c.stationCode);
            //expect(element(by.id("id_date_established")).getAttribute('value')).toEqual(c.dateEstablished);
            expect(element(by.id("id_has_shelter")).isSelected()).toBeTruthy();
            expect(element(by.id("id_latitude")).getAttribute('value')).toEqual(c.latitude);
            expect(element(by.id("id_longitude")).getAttribute('value')).toEqual(c.longitude);

            expect(element(by.id("id_staff_set-0-first_name")).getAttribute('value')).toEqual(c.staff0SetFirstName);
            expect(element(by.id("id_staff_set-0-last_name")).getAttribute('value')).toEqual(c.staff0SetLastName);
            expect(element(by.id("id_staff_set-0-email")).getAttribute('value')).toEqual(c.staff0Email);
            expect(element(by.id("id_staff_set-0-receives_money_distribution_form")).isSelected()).toBeTruthy();

            expect(element(by.id("id_committeemember_set-0-first_name")).getAttribute('value')).toEqual(c.committee0SetFirstName);
            expect(element(by.id("id_committeemember_set-0-last_name")).getAttribute('value')).toEqual(c.committee0SetLastName);
            expect(element(by.id("id_committeemember_set-0-email")).getAttribute('value')).toEqual(c.committee0Email);
            expect(element(by.id("id_committeemember_set-0-receives_money_distribution_form")).isSelected()).toBeTruthy();

            expect(element(by.id("id_location_set-0-name")).getAttribute('value')).toEqual(c.location0SetName);
            expect(element(by.id("id_location_set-0-latitude")).getAttribute('value')).toEqual(c.location0SetLatitude);
            expect(element(by.id("id_location_set-0-longitude")).getAttribute('value')).toEqual(c.location0SetLongitude);
            borderStationPage.closeBorderStation();
            expect(browser.driver.getCurrentUrl()).toContain('/portal/dashboard/');
        });
        it('Edit Border Station', function () {
            borderStationPage.editBorderStation();
            expect(browser.driver.getCurrentUrl()).toContain('/portal/dashboard/');
            borderStationPage.viewBorderStation();

            expect(browser.driver.getCurrentUrl()).toContain('/static_border_stations/border-stations/update/24/');
            expect(element(by.id("id_station_name")).getAttribute('value')).toEqual(c.stationName);

            expect(element(by.id("id_station_code")).getAttribute('value')).toEqual(c.stationCode);
            //expect(element(by.id("id_date_established")).getAttribute('value')).toEqual(c.dateEstablished);
            expect(element(by.id("id_has_shelter")).isSelected()).toBeTruthy();
            expect(element(by.id("id_latitude")).getAttribute('value')).toEqual(c.latitude);
            expect(element(by.id("id_longitude")).getAttribute('value')).toEqual(c.longitude);

            expect(element(by.id("id_staff_set-0-first_name")).getAttribute('value')).toEqual(c.staff0SetFirstName);
            expect(element(by.id("id_staff_set-0-last_name")).getAttribute('value')).toEqual(c.staff0SetLastName);
            expect(element(by.id("id_staff_set-0-email")).getAttribute('value')).toEqual(c.staff0Email);
            expect(element(by.id("id_staff_set-0-receives_money_distribution_form")).isSelected()).toBeTruthy();

            expect(element(by.id("id_committeemember_set-0-first_name")).getAttribute('value')).toEqual(c.committee0SetFirstName);
            expect(element(by.id("id_committeemember_set-0-last_name")).getAttribute('value')).toEqual(c.committee0SetLastName);
            expect(element(by.id("id_committeemember_set-0-email")).getAttribute('value')).toEqual(c.committee0Email);
            expect(element(by.id("id_committeemember_set-0-receives_money_distribution_form")).isSelected()).toBeTruthy();

            expect(element(by.id("id_location_set-0-name")).getAttribute('value')).toEqual(c.location0SetName);
            expect(element(by.id("id_location_set-0-latitude")).getAttribute('value')).toEqual(c.location0SetLatitude);
            expect(element(by.id("id_location_set-0-longitude")).getAttribute('value')).toEqual(c.location0SetLongitude);


            expect(element(by.id("id_staff_set-1-first_name")).getAttribute('value')).toEqual(c.staff1SetFirstName);
            expect(element(by.id("id_staff_set-1-last_name")).getAttribute('value')).toEqual(c.staff1SetLastName);
            expect(element(by.id("id_staff_set-1-email")).getAttribute('value')).toEqual(c.staff1Email);
            expect(element(by.id("id_staff_set-1-receives_money_distribution_form")).isSelected()).toBeTruthy();

            expect(element(by.id("id_committeemember_set-1-first_name")).getAttribute('value')).toEqual(c.committee1SetFirstName);
            expect(element(by.id("id_committeemember_set-1-last_name")).getAttribute('value')).toEqual(c.committee1SetLastName);
            expect(element(by.id("id_committeemember_set-1-email")).getAttribute('value')).toEqual(c.committee1Email);
            expect(element(by.id("id_committeemember_set-1-receives_money_distribution_form")).isSelected()).toBeTruthy();

            expect(element(by.id("id_location_set-1-name")).getAttribute('value')).toEqual(c.location1SetName);
            expect(element(by.id("id_location_set-1-latitude")).getAttribute('value')).toEqual(c.location1SetLatitude);
            expect(element(by.id("id_location_set-1-longitude")).getAttribute('value')).toEqual(c.location1SetLongitude);

            borderStationPage.closeBorderStation();
            expect(browser.driver.getCurrentUrl()).toContain('/portal/dashboard/');
        });
    });
});