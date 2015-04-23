'use strict';

var constants = require('../testConstants.json');

var budgetForm = function () {

    var page = this;

    this.navigateToNewForm = function () {
        browser.get(constants.webAddress + '/static_border_stations/border-stations/update/0/');
        //browser.get(constants.webAddress + '/budget/api/budget_calculations/create/0/');
        //click button
        element.all(by.linkText("New Budget Calculation Form")).click();
    };

    this.fillOutForm = function () {
        // select all input fields and insert '5'
        element(by.id("shelter_rent")).sendKeys('5');
        element(by.id("shelter_water")).sendKeys('5');
        element(by.id("shelter_electricity")).sendKeys('5');
        element(by.id("shelterStartupBool")).click();
        element(by.id("shelter_startup_amount")).sendKeys('5');
        element(by.id("shelter_two_bool")).click();
        element(by.id("shelter_two_amount")).sendKeys('5');
        element(by.id("food_gas_multiplier_before")).sendKeys('5');
        element(by.id("food_gas_number_of_girls")).sendKeys('5');
        element(by.id("food_gas_multiplier_after")).sendKeys('5');
        element(by.id("limbo_multiplier")).sendKeys('5');
        element(by.id("limbo_number_of_girls")).sendKeys('5');
        element(by.id("limbo_number_of_days")).sendKeys('5');
        element(by.id("comm_chair_bool")).click();
        element(by.id("comm_chair_amount")).sendKeys('5');
        element(by.id("comm_manager_bool")).click();
        element(by.id("comm_manager_amount")).sendKeys('5');
        element(by.id("comm_number_of_staff_wt")).sendKeys('5');
        element(by.id("comm_number_of_staff_wt_multiplier")).sendKeys('5');
        element(by.id("comm_each_staff_wt")).sendKeys('5');
        element(by.id("comm_each_staff_wt_multiplier")).sendKeys('5');
        element(by.id("awareness_contact_cards_bool")).click();
        element(by.id("awareness_contact_cards_amount")).sendKeys('5');
        element(by.id("awareness_awareness_party_bool")).click();
        element(by.id("awareness_awareness_party_amount")).sendKeys('5');
        element(by.id("awareness_sign_boards_bool")).click();
        element(by.id("awareness_sign_boards_amount")).sendKeys('5');
        element(by.id("awareness_add_item")).click();
        element(by.id("Z_chair_with_bike_bool")).click();
        element(by.id("travel_chair_with_bike_amount")).sendKeys('5');
        element(by.id("travel_manager_with_bike_bool")).click();
        element(by.id("travel_manager_with_bike_amount")).sendKeys('5');
        element(by.id("travel_number_of_staff_using_bikes")).sendKeys('5');
        element(by.id("travel_number_of_staff_using_bikes_multiplier")).sendKeys('5');
        element(by.id("travel_sending_girls_home_expense")).sendKeys('5');
        element(by.id("travel_motorbike_bool")).click();
        element(by.id("travel_motorbike_amount")).sendKeys('5');
        element(by.id("travel_other")).sendKeys('5');
        element(by.id("travel_add_item")).click();
        element(by.id("supplies_walkie_talkies_bool")).click();
        element(by.id("supplies_walkie_talkies_amount")).sendKeys('5');
        element(by.id("supplies_recorders_bool")).click();
        element(by.id("supplies_recorders_amount")).sendKeys('5');
        element(by.id("supplies_binoculars_bool")).click();
        element(by.id("supplies_binoculars_amount")).sendKeys('5');
        element(by.id("supplies_flashlights_bool")).click();
        element(by.id("supplies_flashlights_amount")).sendKeys('5');
        element(by.id("supplies_add_item")).click();
        element(by.id("admin_number_of_interceptions_last_month")).sendKeys('5');
        element(by.id("admin_number_of_interceptions_last_month_multiplier")).sendKeys('5');
        element(by.id("admin_number_of_interceptions_last_month_adder")).sendKeys('5');
        element(by.id("admin_number_of_meetings_per_month")).sendKeys('5');
        element(by.id("admin_number_of_meetings_per_month_multiplier")).sendKeys('5');
        element(by.id("admin_booth_bool")).click();
        element(by.id("admin_booth_amount")).sendKeys('5');
        element(by.id("admin_registration_bool")).click();
        element(by.id("admin_registration_amount")).sendKeys('5');
        element(by.id("medical_expense")).sendKeys('5');
        element(by.id("misc_number_of_intercepts")).sendKeys('5');
        element(by.id("misc_number_of_intercepts_mult")).sendKeys('5');
        element(by.id("misc_add_item")).click();

        // check all checkboxes
        /*element(by.id("shelterStartupBool")).click();
        element(by.id("shelter_two_bool")).click();
        element(by.id("comm_chair_bool")).click();
        element(by.id("comm_manager_bool")).click();
        element(by.id("awareness_contact_cards_bool")).click();
        element(by.id("awareness_awareness_party_bool")).click();
        element(by.id("awareness_sign_boards_bool")).click();
        element(by.id("Z_chair_with_bike_bool")).click();
        element(by.id("travel_manager_with_bike_bool")).click();
        element(by.id("travel_motorbike_bool")).click();
        element(by.id("supplies_walkie_talkies_bool")).click();
        element(by.id("supplies_recorders_bool")).click();
        element(by.id("supplies_binoculars_bool")).click();
        element(by.id("supplies_flashlights_bool")).click();
        element(by.id("admin_booth_bool")).click();
        element(by.id("admin_registration_bool")).click();*/

        // add items with buttons
        /*element(by.id("awareness_add_item")).click();
        element(by.id("travel_add_item")).click();
        element(by.id("supplies_add_item")).click();
        element(by.id("misc_add_item")).click();*/

    };

    this.submitForm = function () {
        element(by.id("budget_create")).click();
    };

    this.viewForm = function () {
        browser.get(constants.webAddress + '/budget/budget_calculations/');
        element(by.linkText("View")).click();
    };

    this.navigateToForms = function () {
        browser.get(constants.webAddress + '/budget/budget_calculations/');
    };

};

module.exports = new budgetForm();