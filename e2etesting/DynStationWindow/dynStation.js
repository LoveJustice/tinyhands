'use strict';

var c = require('../testConstants.json');

//We need to initialize a google map object in order to use the panTo() method on each lat/lon for each borderStation

var dynStation = function() {
    this.checkStations = function (stationsCount) {
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
                console.log(stationsCount);
                for (var station in stationsCount) {
                    expect(stationsCount[station]).toBe(1);
                }
            });
        });
    };

    this.clickStation = function (station) {

        browser.get(c.webAddress);
        browser.sleep(200);
        $("div[title='Zoom out']").click();
        browser.sleep(500);
        $("area[title='" + station + "']").click();
        //$("area[title='" + station + "']").click();
    };
};
module.exports = new dynStation();
