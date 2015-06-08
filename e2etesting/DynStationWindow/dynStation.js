'use strict';

var c = require('../testConstants.json');
var filloutform = require('../accounts/vifPage.js');


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
        $("area[title='" + station + "']").click();
        browser.sleep(200);
        expect($("div[id='Dynamic " + station + "']").isPresent()).toBe(true);
        expect(element(by.linkText('Subcommittee, Staff, and Locations')).isPresent()).toBe(true);
        expect(element(by.linkText('IRFs')).isPresent()).toBe(true);
        expect(element(by.linkText('VIFs')).isPresent()).toBe(true);

        if(station == "Dang DNG"){
            expect(element(by.id("stationInterception")).getText()).toContain('1');
            expect(element(by.id("staffSet")).getText()).toContain('0');
            expect(element(by.id("shelter")).getText()).toContain('No');
        }

        else{
            expect(element(by.id("stationInterception")).getText()).toContain('0');
            expect(element(by.id("staffSet")).getText()).toContain('0');
            expect(element(by.id("shelter")).getText()).toContain('No');
        }


    };

    this.checkHover = function (station) {
        browser.get(c.webAddress);
        browser.sleep(400);
        browser.actions().mouseMove($("area[title='" + station + "']")).perform();
        browser.sleep(200);
        expect($("div[id='Static " + station + "']").isPresent()).toBe(true);
        expect(element(by.id("stationInterception")).getText()).toContain('0');
        expect(element(by.id("staffSet")).getText()).toContain('0');
        expect(element(by.id("shelter")).getText()).toContain('No');
    };

    this.checkLinks = function (station, code, pk) {
        expect(element(by.linkText('Subcommittee, Staff, and Locations')).getAttribute('href')).toContain('/static_border_stations/border-stations/' + pk );
        expect(element(by.linkText('IRFs')).getAttribute('href')).toContain('data-entry/irfs/search/?search_value=' + code);
        expect(element(by.linkText('VIFs')).getAttribute('href')).toContain('data-entry/vifs/search/?search_value=' + code);
    };
};
module.exports = new dynStation();
