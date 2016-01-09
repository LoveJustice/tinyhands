'use strict';

var navbarPage = function() {
    var page = this; // So if we have any things that create a new scope, we can always reference page without this problems

    page.border_stations_dropdown = element(by.id("border_station_dropdown")).click();
    page.border_stations_in_dropdown = element.all(by.css(".border_station_dropdown_item"));
};

module.exports = navbarPage;
