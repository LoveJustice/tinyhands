'use strict';

var c = require('../testConstants.json');

var moneyDistributionForm = function () {

    this.navigateToMoneyDistributionPage = function () {
        browser.get(c.webAddress + '/budget/budget_calculations/');
        browser.wait(protractor.ExpectedConditions.elementToBeClickable(element(by.linkText("Resend MDF"))), 2000);
        element(by.linkText("Resend MDF")).click();
        browser.wait(protractor.ExpectedConditions.titleIs('Money Distribution PDF | Tiny Hands Dream Suite'), 2000);
    };

    this.toggleEmailAddress = function () {
        var titleElement = element(by.xpath("/html/body/div[2]/div//table/tbody/tr/td[1]/input"));
        titleElement.click();
    };

    this.toggleAllEmailAddresses = function () {
        element.all(by.repeater('staff in main.staff')).then(function(staff) {
            for(var i = 0; i < staff.length; i++) {
                var titleElement = staff[i].element(by.tagName('input'));
                titleElement.click();
                //titleElement.click();
            }
        });
    };

    this.sendEmails = function () {
        element(by.partialLinkText("Send to")).click();
    };

    this.updateBudgetForm = function () {
        element(by.linkText("Update Budget")).click();
    };

};

module.exports = new moneyDistributionForm();