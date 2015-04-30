var constants = require('../testConstants.json');

var tally = function(){
    var self = this;
    
    self.navigateHome = function(){
        return browser.get(constants.webAddress + "/portal/dashboard/");   
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
}

module.exports = new tally();