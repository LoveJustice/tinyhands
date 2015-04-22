var constants = require('../testConstants.json');

var tally = function(){
    var self = this;
    
    self.navigateHome = function(){
        return browser.get(constants.webAddress + "/portal/dashboard/");   
    }
}

module.exports = new tally();