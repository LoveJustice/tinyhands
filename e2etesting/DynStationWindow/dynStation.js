var c = require('../testConstants.json');
var filloutform = require('../accounts/vifPage.js');


var dynStation = function() {

    /*this.checkStationsExist = function (stationsCount) {
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
    };*/

    this.removeEvents = function() {
        browser.actions().mouseMove($("i[class='glyphicon glyphicon-menu-hamburger']")).perform();
        element(by.xpath("/html/body/div[2]/div/div/div/div[3]/ul/li/label/input")).click();
    };

    this.checkClick = function (station) {
        var promises = [];
        console.log(station);
        browser.get(c.webAddress);
        browser.sleep(400);
        this.removeEvents();
        browser.actions().mouseMove($("area[title='" + station + "']")).perform();
        browser.actions().mouseMove($("area[title='" + station + "']")).click().perform();
        browser.sleep(200);
    };

    this.checkHover = function (station) {
        browser.get(c.webAddress);
        browser.sleep(400);
        this.removeEvents();
        browser.actions().mouseMove($("area[title='" + station + "']")).perform();
        browser.sleep(500);
    };
};
module.exports = new dynStation();
