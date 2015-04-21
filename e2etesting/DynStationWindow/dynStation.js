'use strict';

var c = require('../testConstants.json');

var irfPage = function() {
    var page = this;
    
    this.getToIRF = function(){
        browser.get(c.webAddress + '/data-entry/irfs/search/');
        browser.sleep(1000);
        this.link = element(by.id("id_input_new_irf"));
        this.link.click();
        browser.sleep(1000);

    };
};
