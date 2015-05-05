'use strict';

var c = require('../testConstants.json');

//We need to initialize a google map object in order to use the panTo() method on each lat/lon for each borderStation

var dynStation = function() {
    this.checkStationsExist = function (stationsCount) {
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
                ;
            });
        });
    };

    this.checkClick = function (station) {
        var promises = [];

        browser.get(c.webAddress);
        browser.sleep(400);
        //$("div[title='Zoom out']").click(); browser.sleep(500);
        $("area[title='" + station + "']").click();
        browser.sleep(200);
        expect($("div[id='Dynamic " + station + "']").isPresent()).toBe(true);
        expect(element(by.linkText('Subcommittee, Staff, and Locations')).isPresent()).toBe(true);
        expect(element(by.linkText('IRFs')).isPresent()).toBe(true);
        expect(element(by.linkText('VIFs')).isPresent()).toBe(true);

    };

    this.checkHover = function (station) {
        browser.get(c.webAddress);
        browser.sleep(400);
        browser.actions().mouseMove($("area[title='" + station + "']")).perform();
        browser.sleep(200);
        expect($("div[id='Static " + station + "']").isPresent()).toBe(true);
    };

    this.checkLinks = function (station,pk) {
        browser.get(c.webAddress);
        browser.sleep(400);
        $("area[title='" + station + "']").click();
        browser.sleep(200);
        //expect($("a[href='/static_border_stations/border-stations/blaa" + pk + "']").isPresent()).toBe(false);
        //expect(element(by.linkText('Subcommittee, Staff, and Locations')).getAttribute('href')).toEqual('/static_border_stations/border-stations/invalidurl');
        //expect(element(by.linkText('IRFs')).getAttribute('href')).toEqual('http://0.0.0.0:8001/static_border_stations/border-stations/' + pk);
        //expect(element(by.linkText('VIFs')).getAttribute('href')).toEqual('http://0.0.0.0:8001/static_border_stations/border-stations/' + pk);
    };
};
module.exports = new dynStation();
