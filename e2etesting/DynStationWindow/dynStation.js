'use strict';

var c = require('../testConstants.json');


var dynStation = function() {

  this.checkStations = function(stationsCount) {

    console.log("FOO-10");
    var promises=[];

    element.all(by.tagName('area')).each(function(element) {
      console.log("FOO-20");
      promises.push(element.getAttribute("title"));
    }).then(function(){
      protractor.promise.all(promises).then(function(titles) {
	// Check for all 1s
	console.log("All promises are done?");
	titles.forEach(function(title) {
    	  console.log("FOO-30");
    	  // Must be a legitimate title.
    	  expect(title in stationsCount).toBe(true);

    	  // Haven't seen this one before.
    	  expect(stationsCount[title]).toBe(0);
    	  stationsCount[title] += 1;
    	  //console.log(stationsCount);
	});
	console.log(stationsCount);
      });
    });
    console.log("FOO-90");
  };
};

module.exports = new dynStation();
