'use strict';
var c = require('../testConstants.json');
var arr = new Array();


var dynStation = function() {
    var page = this;

    this.countStations = function() {
        $('area[title="Dang DNG"]').click();
    };

/*
    this.findPropertyMarker = function(mTitle) {
        var markers = this.session.elements('css selector', '.gmnoprint map area');
        var title = 'property-' .mTitle;
        for(markers as marker) {
            if(title === marker.attribute('title')) {
                return marker;
            }
        }

        return false;
    };
*/

};

module.exports = new dynStation();