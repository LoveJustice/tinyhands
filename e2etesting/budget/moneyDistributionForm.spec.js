var budgetForm = require('./budgetForm.js');
var loginPage = require('../accounts/loginPage.js');
var c = require('../testConstants.json');
var MDF = require('./moneyDistributionForm.js');

describe('Money Distribution Form', function() {

    beforeEach(function () {
        browser.ignoreSynchronization = true;
        browser.manage().timeouts().implicitlyWait(8000);
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
            browser.sleep(1000);
            browser.waitForAngular();
            MDF.toggleEmailAddress();
            browser.sleep(1000);
            browser.waitForAngular();
            expect(element(by.className("notReceiving")).isPresent()).toBe(true);
            MDF.toggleEmailAddress();
            browser.sleep(1000);
            browser.waitForAngular();
            expect(element(by.className("notReceiving")).isPresent()).toBe(false);
        });

    });

    describe('Redirects to pages correctly', function() {

        it('Returns to budget calc form to update', function() {
            MDF.updateBudgetForm();
            browser.sleep(2000);
            expect(browser.driver.getCurrentUrl()).toContain('api/budget_calculations/update/');
            budgetForm.updateForm();
        });

        it('Goes to the Budget Calc List upon submission', function() {
            browser.sleep(1000);
            browser.waitForAngular();

            MDF.toggleAllEmailAddresses();
            MDF.sendEmails();
        });

    });




});