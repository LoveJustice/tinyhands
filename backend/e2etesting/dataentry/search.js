'use strict';

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

    this.searchKey = function(keys){
		this.searchfield = element(by.className("form-control"));
		this.searchfield.sendKeys(keys);
		this.searchfield.submit();
    };

};

module.exports = new searchIRF();
