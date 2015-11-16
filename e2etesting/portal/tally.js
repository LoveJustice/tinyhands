var constants = require('../testConstants.json');

var tally = function(){
    var self = this;

    self.navigateHome = function(){
        return browser.get(constants.webAddress + "/portal/dashboard/");
    }

    self.calcTime = function(offset) {
      // create Date object for current location
      d = new Date();

      // convert to msec
      // add local time zone offset
      // get UTC time in msec
      utc = d.getTime() + (d.getTimezoneOffset() * 60000);

      // create new Date object for different city
      // using supplied offset
      nd = new Date(utc + (3600000*offset));

      return nd;
    }

    self.dateFormatter = function(date) {
      var day = date.getDate();
      var month = date.getMonth() + 1;
      var year = date.getFullYear();
      var hour = date.getHours();
      var minute = date.getMinutes();

      return month + "/" + day + "/" + year + " " + hour + ":" + minute;
    }

    self.openNewTab = function(){
        return browser.driver.executeScript(function() {
            (function(a){
                document.body.appendChild(a);
                a.setAttribute('href',"http://0.0.0.0:8001" );
                a.dispatchEvent((function(e){
                    e.initMouseEvent("click", true, true, window, 0, 0, 0, 0, 0, true, false, false, false, 0, null);
                    return e;
                }(document.createEvent('MouseEvents'))))
            }(document.createElement('a')));
        });
    }

    self.switchToTab = function(tabNum){
        return browser.getAllWindowHandles().then(function (handles) {
            newWindowHandle = handles[tabNum];
            return browser.switchTo().window(newWindowHandle);
        });
    }

    self.getInterceptions = function(){//grabs interceptions on large tally display
        var interceptions = element.all(by.css('h4.animated.tallyFade')).filter(function(elem, index) {
            return elem.getInnerHtml().then(function(text){
                return text != 'No Interceptions';
            });
        });
        return interceptions;
    }

    self.getInterceptionsSmall = function(){//grabs interceptions on small tally display
        var interceptions = element.all(by.css('h4.ng-binding')).filter(function(elem, index) {
            return elem.getInnerHtml().then(function(text){
                return text != '0' && text.length == 1;
            });
        });
        return interceptions;
    }
}

module.exports = new tally();
