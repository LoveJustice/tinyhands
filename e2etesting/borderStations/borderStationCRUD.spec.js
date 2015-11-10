var c = require('../testConstants.json');
var loginPage = require('../accounts/loginPage.js');
var borderStationPage = require('./borderStation.page.js');
var methods = require('../commonMethods.js');

describe('Border Station CRUD -', function() {
    var BSPage = new borderStationPage();

    beforeEach(function () {
        return browser.ignoreSynchronization = true;
    });

    describe('', function () {
        it('A user can', function () {
            loginPage.logout();
            loginPage.loginAsAdmin();
        });

        it('Create a Border Station', function () {
            BSPage.getToBorderStationCreate();
            expect(browser.driver.getCurrentUrl()).toContain('/static_border_stations/border-stations/create/');
            BSPage.fillOutBorderStation();
            expect(browser.driver.getCurrentUrl()).toContain('/portal/dashboard/');
        });

        it('View a Border Station', function () {
            BSPage.viewBorderStation();
            expect(browser.driver.getCurrentUrl()).toContain('/static_border_stations/border-stations/update/25/');
            expect(BSPage.station_name.getAttribute('value')).toEqual(c.stationName);
            expect(BSPage.station_code.getAttribute('value')).toEqual(c.stationCode);
            expect(BSPage.has_shelter.isSelected()).toBeTruthy();
            expect(BSPage.latitude.getAttribute('value')).toEqual(c.latitude);
            expect(BSPage.longitude.getAttribute('value')).toEqual(c.longitude);

            expect(BSPage.staff0_first_name.getAttribute('value')).toEqual(c.staff0SetFirstName);
            expect(BSPage.staff0_last_name.getAttribute('value')).toEqual(c.staff0SetLastName);
            expect(BSPage.staff0_email.getAttribute('value')).toEqual(c.staff0Email);
            expect(BSPage.staff0_receives_money_distribution_form.isSelected()).toBeTruthy();

            expect(BSPage.committee0_first_name.getAttribute('value')).toEqual(c.committee0SetFirstName);
            expect(BSPage.committee0_last_name.getAttribute('value')).toEqual(c.committee0SetLastName);
            expect(BSPage.committee0_email.getAttribute('value')).toEqual(c.committee0Email);
            expect(BSPage.committee0_receives_money_distribution_form.isSelected()).toBeTruthy();

            expect(BSPage.location0_set_name.getAttribute('value')).toEqual(c.location0SetName);
            expect(BSPage.location0_set_latitude.getAttribute('value')).toEqual(c.location0SetLatitude);
            expect(BSPage.location0_set_longitude.getAttribute('value')).toEqual(c.location0SetLongitude);
            BSPage.closeBorderStation();
            expect(browser.driver.getCurrentUrl()).toContain('/portal/dashboard/');
        });
        it('Edit a Border Station', function () {
            BSPage.editBorderStation();
            expect(browser.driver.getCurrentUrl()).toContain('/portal/dashboard/');
            BSPage.viewBorderStation();

            expect(browser.driver.getCurrentUrl()).toContain('/static_border_stations/border-stations/update/25/');
            expect(BSPage.station_name.getAttribute('value')).toEqual(c.stationName);
            expect(BSPage.station_code.getAttribute('value')).toEqual(c.stationCode);
            expect(BSPage.has_shelter.isSelected()).toBeTruthy();
            expect(BSPage.latitude.getAttribute('value')).toEqual(c.latitude);
            expect(BSPage.longitude.getAttribute('value')).toEqual(c.longitude);

            expect(BSPage.staff0_first_name.getAttribute('value')).toEqual(c.staff0SetFirstName);
            expect(BSPage.staff0_last_name.getAttribute('value')).toEqual(c.staff0SetLastName);
            expect(BSPage.staff0_email.getAttribute('value')).toEqual(c.staff0Email);
            expect(BSPage.staff0_receives_money_distribution_form.isSelected()).toBeTruthy();

            expect(BSPage.committee0_first_name.getAttribute('value')).toEqual(c.committee0SetFirstName);
            expect(BSPage.committee0_last_name.getAttribute('value')).toEqual(c.committee0SetLastName);
            expect(BSPage.committee0_email.getAttribute('value')).toEqual(c.committee0Email);
            expect(BSPage.committee0_receives_money_distribution_form.isSelected()).toBeTruthy();

            expect(BSPage.location0_set_name.getAttribute('value')).toEqual(c.location0SetName);
            expect(BSPage.location0_set_latitude.getAttribute('value')).toEqual(c.location0SetLatitude);
            expect(BSPage.location0_set_longitude.getAttribute('value')).toEqual(c.location0SetLongitude);


            expect(BSPage.staff1_first_name.getAttribute('value')).toEqual(c.staff1SetFirstName);
            expect(BSPage.staff1_last_name.getAttribute('value')).toEqual(c.staff1SetLastName);
            expect(BSPage.staff1_email.getAttribute('value')).toEqual(c.staff1Email);
            expect(BSPage.staff1_receives_money_distribution_form.isSelected()).toBeTruthy();

            expect(BSPage.committee1_first_name.getAttribute('value')).toEqual(c.committee1SetFirstName);
            expect(BSPage.committee1_last_name.getAttribute('value')).toEqual(c.committee1SetLastName);
            expect(BSPage.committee1_email.getAttribute('value')).toEqual(c.committee1Email);
            expect(BSPage.committee1_receives_money_distribution_form.isSelected()).toBeTruthy();

            expect(BSPage.location1_set_name.getAttribute('value')).toEqual(c.location1SetName);
            expect(BSPage.location1_set_latitude.getAttribute('value')).toEqual(c.location1SetLatitude);
            expect(BSPage.location1_set_longitude.getAttribute('value')).toEqual(c.location1SetLongitude);

            BSPage.closeBorderStation();
            expect(browser.driver.getCurrentUrl()).toContain('/portal/dashboard/');
        });
    });

    describe('Create Border Station', function() {

        it('fails when receives money distribution form checked with no email', function() {
            browser.get(c.webAddress + '/static_border_stations/border-stations/create/').then(function() {
                return expect(browser.driver.getCurrentUrl()).toContain('/static_border_stations/border-stations/create/');
            }).then(function() {
                return BSPage.fillOutBorderStationWithNoEmail();
            }).then(function() {
                expect(browser.driver.getCurrentUrl()).toContain('/static_border_stations/border-stations/create/');
            }).then(function() {
                expect(element.all(by.cssContainingText('.alert-danger', 'Email cannot be blank when receives money distribution form is checked.'))
                .count()).toEqual(2);
            });


        });
    });

    describe('Update Border Station', function() {

        it('fails when receives money distribution form checked with no email', function() {
            BSPage.editBorderStationWithNoEmail().then(function() {
                return expect(browser.driver.getCurrentUrl()).toContain('/static_border_stations/border-stations/update/' + 25 + '/');
            }).then(function() {
                expect(element.all(by.cssContainingText('.alert-danger', 'Email cannot be blank when receives money distribution form is checked.')).count()).toEqual(2);
            });
        });
    });

});
