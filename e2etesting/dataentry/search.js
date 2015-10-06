var constants = require('../testConstants.json');
var loginPage = require('../accounts/loginPage.js');

var searchIRF = function(){

    var page = this;

    this.gotoIRFSearch = function(){
		browser.get(constants.webAddress + '/data-entry/irfs/search/');
	};

	this.gotoVIFSearch = function(){
		browser.get(constants.webAddress + '/data-entry/vifs/search/');
	};

    this.searchKey = function(keys, xpath){
		this.searchfield = element(by.xpath(xpath));
		this.searchfield.sendKeys(keys);
    };
};

module.exports = new searchIRF();
