var c = require('../testConstants.json');
var loginPage = require('../accounts/loginPage.js');
var borderStations = require('../fixtures/border_stations.json');
var dynStation = require('./dynStation.js');
var stationsFound = new Array();



var stationsCount = new Object();
var stationsCoords = new Object();
for (var i = 0;  i < borderStations.length; i++) {
  var station = JSON.parse(JSON.stringify(borderStations[i]));
  var name = station.fields.station_name + " " + station.fields.station_code;
  var lat = stations.fields.latitude;
  var lon = stations.fields.longitude;
  stationsCount[name] = 0;
  stationsCoords[name]=[lat,lon];

}

dynStation.initialize();

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
        dynStation.checkStations(stationsCount);
    });
    it('marker is clickable', function() {
        for(var station in stationsCount) {
            dynStation.clickStation(station);
        };
    });
  });
});
