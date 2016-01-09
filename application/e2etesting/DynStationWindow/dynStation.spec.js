var c = require('../testConstants.json');
var loginPage = require('../accounts/loginPage.js');
var borderStations = require('../fixtures/border_stations.json');
var dynStation = require('./dynStation.js');
var fullDict = new Object();



var stationsCode = new Object();
var stationsCount = new Object();
var stationsPk = new Object();
for (var i = 0;  i < borderStations.length; i++) {
    var station = JSON.parse(JSON.stringify(borderStations[i]));
    var name = station.fields.station_name + " " + station.fields.station_code;
    var code = station.fields.station_code;
    stationsCount[name] = 0;
    stationsPk[name] = station.pk;
    stationsCode[name] = code;

}

describe('Dynamic Station Window', function() {

    beforeEach(function () {
        return browser.ignoreSynchronization = true;
    });

    describe('Dynamic Station Window Tests', function () {
        it('accepts credentials', function () {
            loginPage.logout();
            loginPage.loginAsAdmin();
            browser.sleep(1000);
        });
    });

    describe('Test Marker Functionality', function () {

        it('marker exists', function () {
            //dynStation.checkStationsExist(stationsCount);
            var promises = [];

            element.all(by.tagName('area')).each(function (area) {
                promises.push(area.getAttribute("title"));
            }).then(function () {
                protractor.promise.all(promises).then(function (titles) {
                    // Check for all 1s
                    titles.forEach(function (title) {
                        // Must be a legitimate title.
                        expect(title in stationsCount).toBe(true);

                        // Haven't seen this one before.
                        expect(stationsCount[title]).toBe(0);
                        stationsCount[title] += 1;
                        //console.log(stationsCount);
                    });
                    //console.log(stationsCount);
                    for (var station in stationsCount) {
                        expect(stationsCount[station]).toBe(1);
                    }
                });
            });
        });

        it('marker is clickable and links are correct', function() {
            for (var station in stationsCount) {
                //console.log(station);
                dynStation.checkClick(station);
                expect($("div[id='Dynamic" + station.slice(-3) + "']").isPresent()).toBe(true);
                expect(element(by.linkText('Subcommittee, Staff, and Locations')).isPresent()).toBe(true);
                expect(element(by.linkText('IRFs')).isPresent()).toBe(true);
                expect(element(by.linkText('VIFs')).isPresent()).toBe(true);
                if(station == "Dang DNG") {
                    expect(element(by.id("stationInterception")).getText()).toContain('1');
                }
                else {
                    expect(element(by.id("stationInterception")).getText()).toContain('0');
                }
                expect(element(by.id("staffset")).getText()).toContain('0');
                expect(element(by.id("shelter")).getText()).toContain('No');

                //dynStation.checkLinks(station, stationsCode[station], stationsPk[station]);
                expect(element(by.linkText('Subcommittee, Staff, and Locations')).getAttribute('href')).toContain('/static_border_stations/border-stations/' + stationsPk[station]);
                expect(element(by.linkText('IRFs')).getAttribute('href')).toContain('data-entry/irfs/search/?search_value=' + stationsCode[station]);
                expect(element(by.linkText('VIFs')).getAttribute('href')).toContain('data-entry/vifs/search/?search_value=' + stationsCode[station]);
            }
        }, 50000);

        it('marker is hoverable', function() {
            for (var station in stationsCount) {
                dynStation.checkHover(station);
                expect(element(by.id("Static"+station.slice(-3))).isPresent()).toBe(true);
                if(station == "Dang DNG") {
                    expect(element(by.id("stationInterception")).getText()).toContain('1');
                }
                else {
                    expect(element(by.id("stationInterception")).getText()).toContain('0');
                }
                expect(element(by.id("staffset")).getText()).toContain('0');
                expect(element(by.id("shelter")).getText()).toContain('No');
            }
        }, 50000);
    });

});
