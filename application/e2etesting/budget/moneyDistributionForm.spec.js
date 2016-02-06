var budgetForm = require('./budgetForm.js');
var loginPage = require('../accounts/loginPage.js');
var constants = require('../testConstants.json');
var MDF = require('./moneyDistributionForm.js');

describe('Money Distribution Form', function() {

    beforeEach(function () {
        return browser.ignoreSynchronization = true;
    });

    describe('Login', function() {

        it('logs in', function() {
            loginPage.loginAsAdmin();
            expect(browser.driver.getCurrentUrl()).toContain('portal/dashboard');
        });

    });

    describe('Email Functionality', function() {

        it('toggles e-mail addresses active/inactive', function() {
            MDF.navigateToMoneyDistributionPage();
            MDF.toggleEmailAddress();
            expect(element(by.className("notReceiving")).isPresent()).toBe(true);
            MDF.toggleEmailAddress();
            expect(element(by.className("notReceiving")).isPresent()).toBe(false);
        });

    });

    describe('Redirects to pages correctly', function() {

        it('Returns to budget calc form to update', function() {
            MDF.updateBudgetForm();
            expect(browser.driver.getCurrentUrl()).toContain('api/budget_calculations/update/');
            budgetForm.updateForm();
        });

        it('Goes to the Budget Calc List upon submission', function() {
            MDF.toggleAllEmailAddresses();
            MDF.sendEmails();
            //expect(browser.driver.getCurrentUrl()).toContain('portal/dashboard');
        });

    });




});