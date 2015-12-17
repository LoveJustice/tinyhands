var c = require('../testConstants.json');
var loginPage = require('../accounts/loginPage.js');
var borderStation = require('./borderStation.js');

describe('Border Stations - Close a Station - ', function() {

    beforeEach(function () {
        browser.ignoreSynchronization = true;
        browser.manage().timeouts().implicitlyWait(7000);
    });

    describe('', function () {
        it('Log in', function () {
            loginPage.logout();
            loginPage.loginAsAdmin();
        });

        it('create own test station', function () {
            borderStation.getToBorderStationCreate();
            borderStation.fillOutBorderStation("zzz closedTest", "CLT");
        });

        it('the close station button exists', function() {
            browser.get(c.webAddress);
            element(by.id("border_station_dropdown")).click();
            element.all(by.css(".border_station_dropdown_item")).last().click();

            browser.wait(protractor.ExpectedConditions.titleIs("Border Stations | Tiny Hands Dream Suite"), 7000);
            browser.wait(protractor.ExpectedConditions.presenceOf(element(by.css('[ng-click="bsCtrl.changeStationStatus()"]'))), 7000);
            expect(element(by.css('[ng-click="bsCtrl.changeStationStatus()"]')).isPresent()).toBe(true);
        });

        it('the button toggles between open and closed', function() {

            //TODO finish changing this file to use borderStation.js
            var button = element(by.css('[ng-click="bsCtrl.changeStationStatus()"]'))
            expect(button.getAttribute('class')).toContain('btn-success');
            button.click();
            expect(button.getAttribute('class')).toContain('btn-danger');
        });

        it('the border station is taken out of dropdown', function() {
            borderStation.saveForm();

            //Seems that the dropdown only updates once you navigate away from the border station page after saving.
            browser.get(c.webAddress);

            element(by.id("border_station_dropdown")).click();
            expect(element.all(by.css(".border_station_dropdown_item")).last().getText()).not.toBe("zzz closedTest");
        });
    });
});
