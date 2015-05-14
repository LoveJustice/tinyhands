var budgetForm = require('./budgetForm.js');
var loginPage = require('../accounts/loginPage.js');
var constants = require('../testConstants.json');

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
            browser.sleep(500);
        });

        it('calculates values correctly ', function () {
            // fill out form
            browser.ignoreSynchronization = false;
            budgetForm.fillOutForm();

            // expect totals to be certain values
            expect(element(by.id('staffTotal')).getAttribute("value")).toBe('100');
            expect(element(by.binding("main.shelterTotal()")).getText()).toBe('900');
            expect(element(by.binding("main.foodTotal()")).getText()).toBe('2000');
            expect(element(by.binding("main.commTotal()")).getText()).toBe('900');
            expect(element(by.binding("main.awarenessTotalValue")).getText()).toBe('700');
            expect(element(by.binding("main.travelTotalValue")).getText()).toBe('1050');
            expect(element(by.binding("main.suppliesTotalValue")).getText()).toBe('1100');
            expect(element(by.binding("main.adminTotal()")).getText()).toBe('750');
            expect(element(by.binding("main.medicalTotal()")).getText()).toBe('100');
            expect(element(by.binding("main.miscTotalValue")).getText()).toBe('600');
            expect(element(by.binding("main.bunchTotal()")).getText()).toBe('3500');
            expect(element(by.binding("main.foodAndShelterTotal()")).getText()).toBe('2900');
            expect(element(by.binding("main.stationTotal()")).getText()).toBe('8300');
        }, 500000);

        it('redirects on submit to Money Distribution Form', function () {
            //budgetForm.navigateToForms();
            budgetForm.submitForm();
            browser.sleep(1000);
            expect(browser.driver.getCurrentUrl()).toContain('budget_calculations/money_distribution');
        });

        it('should show form in budget calculations list', function () {
            browser.sleep(1000);
            browser.get(constants.webAddress + '/budget/budget_calculations/');
            browser.sleep(500);
            var x = new Date();
            var monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
            expect(element(by.css("#budget_list > div.container > table > tbody > tr:nth-child(1) > td:nth-child(1)")).getText()).toBe('Test Station');
            expect(element(by.css("#budget_list > div.container > table > tbody > tr:nth-child(1) > td:nth-child(2)")).getText()).toBe('AAA');
            expect(element(by.css("#budget_list > div.container > table > tbody > tr:nth-child(1) > td:nth-child(3)")).getText()).toBe(monthNames[x.getMonth()] + " " + x.getFullYear());
        });
    }, 500000);

    describe('viewing form', function () {
        it('all inputs are disabled', function () {
            budgetForm.viewForm();
            browser.sleep(1000);

            expect(element(by.id("month_year"))).toBeDefined();
            expect(element(by.id("shelter_rent")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("shelter_water")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("shelter_electricity")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("shelterStartupBool")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("shelter_startup_amount")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("shelter_two_bool")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("shelter_two_amount")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("food_gas_multiplier_before")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("food_gas_number_of_girls")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("food_gas_multiplier_after")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("limbo_multiplier")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("limbo_number_of_girls")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("limbo_number_of_days")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("comm_chair_bool")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("comm_chair_amount")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("comm_manager_bool")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("comm_manager_amount")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("comm_number_of_staff_wt")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("comm_number_of_staff_wt_multiplier")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("comm_each_staff_wt")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("comm_each_staff_wt_multiplier")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("awareness_contact_cards_bool")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("awareness_contact_cards_amount")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("awareness_awareness_party_bool")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("awareness_awareness_party_amount")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("awareness_sign_boards_bool")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("awareness_sign_boards_amount")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("travel_chair_with_bike_bool")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("travel_chair_with_bike_amount")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("travel_manager_with_bike_bool")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("travel_manager_with_bike_amount")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("travel_number_of_staff_using_bikes")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("travel_number_of_staff_using_bikes_multiplier")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("travel_sending_girls_home_expense")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("travel_motorbike_bool")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("travel_motorbike_amount")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("travel_other")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("supplies_walkie_talkies_bool")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("supplies_walkie_talkies_amount")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("supplies_recorders_bool")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("supplies_recorders_amount")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("supplies_binoculars_bool")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("supplies_binoculars_amount")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("supplies_flashlights_bool")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("supplies_flashlights_amount")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("admin_number_of_interceptions_last_month")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("admin_number_of_interceptions_last_month_multiplier")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("admin_number_of_interceptions_last_month_adder")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("admin_number_of_meetings_per_month")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("admin_number_of_meetings_per_month_multiplier")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("admin_booth_bool")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("admin_booth_amount")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("admin_registration_bool")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("admin_registration_amount")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("medical_expense")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("misc_number_of_intercepts")).getAttribute('disabled')).toBe('true');
            expect(element(by.id("misc_number_of_intercepts_mult")).getAttribute('disabled')).toBe('true');
        });
    });

    describe('editing form', function () {
        it('all inputs are enabled', function () {
            budgetForm.editForm();
            browser.sleep(1000);

            expect(element(by.id("month_year"))).toBeDefined();
            expect(element(by.id("shelter_rent")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("shelter_water")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("shelter_electricity")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("shelterStartupBool")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("shelter_startup_amount")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("shelter_two_bool")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("shelter_two_amount")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("food_gas_multiplier_before")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("food_gas_number_of_girls")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("food_gas_multiplier_after")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("limbo_multiplier")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("limbo_number_of_girls")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("limbo_number_of_days")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("comm_chair_bool")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("comm_chair_amount")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("comm_manager_bool")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("comm_manager_amount")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("comm_number_of_staff_wt")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("comm_number_of_staff_wt_multiplier")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("comm_each_staff_wt")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("comm_each_staff_wt_multiplier")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("awareness_contact_cards_bool")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("awareness_contact_cards_amount")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("awareness_awareness_party_bool")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("awareness_awareness_party_amount")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("awareness_sign_boards_bool")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("awareness_sign_boards_amount")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("travel_chair_with_bike_bool")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("travel_chair_with_bike_amount")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("travel_manager_with_bike_bool")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("travel_manager_with_bike_amount")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("travel_number_of_staff_using_bikes")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("travel_number_of_staff_using_bikes_multiplier")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("travel_sending_girls_home_expense")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("travel_motorbike_bool")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("travel_motorbike_amount")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("travel_other")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("supplies_walkie_talkies_bool")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("supplies_walkie_talkies_amount")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("supplies_recorders_bool")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("supplies_recorders_amount")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("supplies_binoculars_bool")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("supplies_binoculars_amount")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("supplies_flashlights_bool")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("supplies_flashlights_amount")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("admin_number_of_interceptions_last_month")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("admin_number_of_interceptions_last_month_multiplier")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("admin_number_of_interceptions_last_month_adder")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("admin_number_of_meetings_per_month")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("admin_number_of_meetings_per_month_multiplier")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("admin_booth_bool")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("admin_booth_amount")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("admin_registration_bool")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("admin_registration_amount")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("medical_expense")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("misc_number_of_intercepts")).getAttribute('enabled')).toBe(null);
            expect(element(by.id("misc_number_of_intercepts_mult")).getAttribute('enabled')).toBe(null);
        });
    });
});