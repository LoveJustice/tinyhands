'use strict';

var constants = require('../testConstants.json');

var moneyDistributionForm = function () {



    this.navigateToMoneyDistributionPage = function () {
        browser.get(constants.webAddress + '/budget/budget_calculations/');
        element(by.linkText("Resend MDF")).click();
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
                titleElement.click();
            }
        });

    };

    this.sendEmails = function () {
        //browser.ignoreSynchronization = false;
        element(by.buttonText("Send to Selected Staff and Members")).click();
        browser.sleep(7000);
    };

    this.updateBudgetForm = function () {
        element(by.linkText("Update Budget")).click();
    };

};

module.exports = new moneyDistributionForm();