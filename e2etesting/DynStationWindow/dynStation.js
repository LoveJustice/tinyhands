'use strict';

var c = require('../testConstants.json');


var dynStation = function() {

/*  this.checkClick = function(){
      var promises = [];
      element.all(by.tagName('area')).each(function(element) {
          console.log("Found A Marker");
          promises.push(element);
          }).then(function(){
          protractor.promise.all(promises).then(function(stations){
              stations.forEach(function(station) {
                  station.click().then(function(){
                      expect(element(by.class("dynamicInfoWindow"))).isPresent().toBe(true);
                  });

              });
          });
      });
          console.log("I was clicked");

    };*/



  this.checkHover = function() {
      //ptor.actions().mouseMove(ptor.findElement(protractor.B.title('DNG'))).perform();
      ptor.actions().mouseMove(element.all(by.tagName('area'))).perform();
  }


  this.checkStations = function(stationsCount) {
      var promises=[];
      element.all(by.tagName('area')).each(function(area) {
          promises.push(area.getAttribute("title"));
      }).then(function(){
          protractor.promise.all(promises).then(function(titles) {

              // Check for all 1s
              titles.forEach(function(title) {
                  // Must be a legitimate title.
                  expect(title in stationsCount).toBe(true);

                  // Haven't seen this one before.
                  expect(stationsCount[title]).toBe(0);
                  stationsCount[title] += 1;
              });
              for( var station in stationsCount){
                  expect(stationsCount[station]).toBe(1);
              }
              return stationsCount
          });
      });
  };

  this.clickStations = function (stationsCount){
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
          }
  }

};

module.exports = new dynStation();
