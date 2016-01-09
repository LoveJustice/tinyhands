var constants = require('../testConstants.json');
var loginPage = require('../accounts/loginPage.js');

var searchIRF = function(){

    var page = this;

    this.gotoIRFSearch = function(){
		browser.get(constants.webAddress + '/data-entry/irfs/');
	};

	this.gotoVIFSearch = function(){
		browser.get(constants.webAddress + '/data-entry/vifs/');
	};

    this.searchKey = function(keys, model){
		this.searchfield = element(by.model(model));
		this.searchfield.sendKeys(keys);
    };
};

module.exports = new searchIRF();
