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

};

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
            dynStation.checkStationsExist(stationsCount);
        });

        it('marker is clickable and links are correct', function() {
            for (var station in stationsCount) {
                dynStation.checkClick(station);
                dynStation.checkLinks(station, stationsCode[station], stationsPk[station]);
            };
        }, 50000);

        it('marker is hoverable', function() {
            for (var station in stationsCount) {
                dynStation.checkHover(station);
            };
        }, 50000);



    });

});
