'use strict';

var constants = require('../testConstants.json');
var methods = require('../commonMethods.js');

var moneyDistributionForm = function () {

    this.navigateToMoneyDistributionPage = function () {
        browser.get(constants.webAddress + '/budget/budget_calculations/');
        //element(by.linkText("Resend MDF")).click();
        methods.click(element(by.linkText("Resend MDF")));
    };

    this.toggleEmailAddress = function () {
        element.all(by.repeater('staff in main.staff')).then(function(staff) {
            var titleElement = staff[0].element(by.tagName('input'));
            titleElement.click();
        });
    };

    this.toggleAllEmailAddresses = function () {
        element.all(by.repeater('staff in main.staff')).then(function(staff) {
            for(var i = 0; i < staff.length; i++) {
                var titleElement = staff[i].element(by.tagName('input'));
                methods.click(titleElemtn);
                //titleElement.click();
            }
        });
    };

    this.sendEmails = function () {
        methods.click(element(by.partialLinkText("Send to")));
        element(by.partialLinkText("Send to")).click();
    };

    this.updateBudgetForm = function () {
        //element(by.linkText("Update Budget")).click();
        methods.click(element(by.linkText("Update Budget")));
    };

};

module.exports = new moneyDistributionForm();