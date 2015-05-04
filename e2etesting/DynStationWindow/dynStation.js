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
            });
        });
    };

    this.checkClick = function (stationsCount) {
        for(var station in stationsCount) {
            browser.get(c.webAddress);
            browser.sleep(800);
            //$("div[title='Zoom out']").click();
            //browser.sleep(500);
            $("area[title='" + station + "']").click();
            //$("area[title='" + station + "']").click();
            expect($("div[id='Dynamic "+ station + "']").isPresent()).toBe(true);
            /*
            element(by.linkText('Subcommittee, Staff, and Locations')).then(function (link) {
                link.click().then(function () {
                    browser.sleep(800);
                    console.log("HERE");
                    expect(browser.driver.getCurrentUrl()).toContain('/static_border_stations/border-stations/');
                });
                //browser.get(c.webAddress);
                //console.log("DONE");
            });
            */
        };
    };

    this.checkHover = function(stationsCount) {
    /*
        for(var station in stationsCount) {
            browser.get(c.webAddress);
            browser.sleep(800);
            //ptor.actions().
            //    mouseMove(ptor.findElement(protractor.byid))
            $("area[title='" + station + "']").mouseover();
            expect($("div[id='Static "+ station + "']").isPresent()).toBe(true);
        };
    */
    };

    this.clickStations = function (stationsCount){
        /*
        var mapOptions = {
            center: { lat: 28.394857, lng: 84.124008},
            zoom: 3,
            streetViewControl: false
        };
        var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
        */
        var baz = "area[title='Bhadrapur BHD']";
        element(by.css(baz)).click().then(function () {
            console.log("Clicked the first one");
        });
        //$("area[title='Dang DNG']").click();
        console.log(stationsCount);
        for(var myStation in stationsCount){
            var foo = "area[title='" + myStation + "']";
            console.log(foo);
            var my_element = browser.driver.findElement(By.css(foo));
            debugger;
            my_element.scrollIntoView();
            ptor.sleep(500);
            my_element.click().then(function () {
                console.log("Clicked");
            });
        };
    };
};
module.exports = new dynStation();
