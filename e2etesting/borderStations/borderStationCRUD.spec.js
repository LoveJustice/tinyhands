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
            browser.sleep(1000);
        });

        it('Create IRF', function () {
            borderStationPage.getToBoarderStationCreate();
            expect(browser.driver.getCurrentUrl()).toContain('static_border_stations/border-stations/create/');
            browser.sleep(10000);
            borderStationPage.fillOutBoarderStation();
            //expect(browser.driver.getCurrentUrl()).toContain('data-entry/irfs/search/');
            browser.sleep(1000);
        });

    });
});