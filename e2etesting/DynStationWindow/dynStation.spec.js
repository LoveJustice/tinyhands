var c = require('../testConstants.json');
var loginPage = require('../accounts/loginPage.js');
var borderStations = require('../fixtures/border_stations.json');
var dynStation = require('./dynStation.js');
var stationsFound = new Array();

var stationsCount = new Object();
for (var i = 0;  i < borderStations.length; i++) {
  var station = JSON.parse(JSON.stringify(borderStations[i]));
  var name = station.fields.station_name + " " + station.fields.station_code;
  stationsCount[name] = 0;
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

  describe('Test Marker Exists', function () {
    it('marker exists', function () {
      console.log("BEFORE\n", stationsCount);
      dynStation.checkStations(stationsCount);
      console.log("AFTER\n", stationsCount);
    });
  });

});
