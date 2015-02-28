'use strict';

//var constants = require('../testConstants.json);
var loginPage = require('../accounts/loginPage.js');

var searchIRF = function(){

    var page = this;

	this.gotoSearch = function(){
		browser.get('http://0.0.0.0:8000/data-entry/irfs/search/');
	};

    this.searchKey = function(keys){
		this.searchfield = element(by.className("form-control"));
		this.searchfield.sendKeys(keys);
		this.searchfield.submit();
    };

};

module.exports = new searchIRF();
