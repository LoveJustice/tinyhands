var c = require('../testConstants.json');
var loginPage = require('../accounts/loginPage.js');
var borderStations = require('../fixtures/border_stations.json');
var dynStation = require('./dynStation.js');
var stationsFound = new Array();
var fullDict = new Object();



var stationsCount = new Object();
var stationsCoords = new Object();
for (var i = 0;  i < borderStations.length; i++) {
  var station = JSON.parse(JSON.stringify(borderStations[i]));
  var name = station.fields.station_name + " " + station.fields.station_code;
  var lat = station.fields.latitude;
  var lon = station.fields.longitude;
  stationsCount[name] = 0;
  stationsCoords[name]=[lat,lon];

}

//dynStation.initialize();

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
    it('marker is clickable', function() {
        dynStation.checkClick(stationsCount);
    });
    it('marker is hoverable', function() {
        dynStation.checkHover(stationsCount);
    });
});

/*
  describe('Click Box is Present', function () {
      it('box exists', function () {
          console.log("About to check for boxes");

          dynStation.clickStations(stationsCount);

          console.log("Done checking for boxes");

      });
  });

/*  describe('Hover Box is Shown', function () {
      it('hover box is shown', function (){
          console.log("About to check hover boxes");
          dynStation.checkHover();
          expect(element(by.id("StaticDNG")).isPresent()).toBe(true);
      })

  })*/

});
