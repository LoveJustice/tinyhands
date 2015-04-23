var budgetForm = require('./budgetForm.js');
var loginPage = require('./loginPage.js');

describe('Budget Calculation', function() {
    beforeEach(function () {
       return browser.ignoreSynchronization = true;
    });

    describe('admin can login', function () {
       it('accepts credentials', function () {
           loginPage.loginAsAdmin();
           expect(browser.driver.getCurrentUrl()).toContain('portal/dashboard');
       });
    });

    describe('form creation', function () {
        it('goes to new form', function () {
            budgetForm.navigateToNewForm();
            expect(browser.driver.getCurrentUrl()).toContain('/budget/api/budget_calculations/create/');
        });

        it('calculates values correctly ', function () {
            // fill out form
            budgetForm.fillOutForm();

            // expect totals to be certain values
            expect(element(by.binding("main.commTotal()")).getText()).toBe('60');
            expect(element(by.binding("main.travelTotalValue")).getText()).toBe('50');
            expect(element(by.binding("main.adminTotal()")).getText()).toBe('65');
            expect(element(by.binding("main.medicalTotal()")).getText()).toBe('5');
            expect(element(by.binding("main.miscTotalValue")).getText()).toBe('25');
            expect(element(by.binding("main.bunchTotal()")).getText()).toBe('205');
            expect(element(by.binding("main.shelterTotal()")).getText()).toBe('25');
            expect(element(by.binding("main.foodTotal()")).getText()).toBe('250');
            expect(element(by.binding("main.foodAndShelterTotal()")).getText()).toBe('275');
            expect(element(by.binding("main.awarenessTotalValue")).getText()).toBe('15');
            expect(element(by.binding("main.suppliesTotalValue")).getText()).toBe('20');
            expect(element(by.binding("main.stationTotal()")).getText()).toBe('515');
        });

        it('redirects on submit', function () {
            //budgetForm.navigateToForms();
            budgetForm.submitForm();
            browser.sleep(2000);
            expect(browser.driver.getCurrentUrl()).toContain('budget/budget_calculation');
        });
    });

    describe('viewing form', function () {
        it('inputs are disabled', function () {
            budgetForm.viewForm();
            browser.sleep(2000);
            expect(element(by.id("shelter_rent")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("food_gas_multiplier_before")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("comm_chair_amount")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("awareness_contact_cards_amount")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("travel_chair_with_bike_amount")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("supplies_walkie_talkies_amount")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("admin_number_of_interceptions_last_month")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("medical_expense")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("misc_number_of_intercepts")).getAttribute('disabled')).toBe('true');
        });
    });

});