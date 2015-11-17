var c = require('../testConstants.json');
var loginPage = require('../accounts/loginPage.js');
var borderStationPage = require('./borderStation.page.js');

describe('Border Stations - Close a Station - ', function() {
    var BSPage = new borderStationPage();

    beforeEach(function () {
        return browser.ignoreSynchronization = true;
    });

    describe('', function () {
        it('Log in', function () {
            loginPage.logout();
            loginPage.loginAsAdmin();
        });

        it('create own test station', function () {
            BSPage.getToBorderStationCreate();
            BSPage.fillOutBorderStation("zzz closedTest", "CLT");
        });

        it('the close station button exists', function() {
            browser.get(c.webAddress);
            element(by.id("border_station_dropdown")).click();
            element.all(by.css(".border_station_dropdown_item")).last().click();

            expect(BSPage.stationClosedButton.isPresent()).toBe(true);
        });

        it('the button toggles between open and closed', function() {
            expect(BSPage.stationClosedButtonLabel.getAttribute('class')).toContain('btn-success');
            BSPage.stationClosedButton.click();
            expect(BSPage.stationClosedButtonLabel.getAttribute('class')).toContain('btn-danger');
        });

        it('the border station is taken out of dropdown', function() {
            BSPage.border_station_update_button.click();

            element(by.id("border_station_dropdown")).click();
            expect(element.all(by.css(".border_station_dropdown_item")).last().getText()).not.toBe("zzz closedTest");
        });
    });
});
