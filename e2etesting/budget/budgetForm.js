'use strict';

var constants = require('../testConstants.json');

var budgetForm = function () {

    var page = this;

    this.navigateToNewForm = function () {
        browser.get(constants.webAddress + '/static_border_stations/border-stations/update/24/');
        //click button
        element.all(by.linkText("New Budget Calculation Form")).click();
    };

    this.fillOutForm = function () {
        // select all input fields and insert '5'

        browser.sleep(1000);
        browser.executeScript('document.getElementById("month_year").value = "2015-07"');
        browser.executeScript('$("#month_year").trigger("change");');
        browser.sleep(1000);
        element(by.model("form.salary")).clear().sendKeys('100');
        element(by.id("shelter_rent")).clear().sendKeys('100');
        element(by.id("shelter_water")).clear().sendKeys('200');
        element(by.id("shelter_electricity")).clear().sendKeys('300');
        element(by.id("shelterStartupBool")).click();
        element(by.id("shelter_startup_amount")).clear().sendKeys('100');
        element(by.id("shelter_two_bool")).click();
        element(by.id("shelter_two_amount")).clear().sendKeys('200');
        element(by.id("food_gas_multiplier_before")).clear().sendKeys('100');
        element(by.id("food_gas_number_of_girls")).clear().sendKeys('4');
        element(by.id("food_gas_multiplier_after")).clear().sendKeys('2');
        element(by.id("limbo_multiplier")).clear().sendKeys('200');
        element(by.id("limbo_number_of_girls")).clear().sendKeys('2');
        element(by.id("limbo_number_of_days")).clear().sendKeys('3');
        element(by.id("comm_chair_bool")).click();
        element(by.id("comm_chair_amount")).clear().sendKeys('100');
        element(by.id("comm_manager_bool")).click();
        element(by.id("comm_manager_amount")).clear().sendKeys('200');
        element(by.id("comm_number_of_staff_wt")).clear().sendKeys('5');
        element(by.id("comm_number_of_staff_wt_multiplier")).clear().sendKeys('20');
        element(by.id("comm_each_staff_wt")).clear().sendKeys('100');
        element(by.id("comm_each_staff_wt_multiplier")).clear().sendKeys('5');
        element(by.id("awareness_contact_cards_bool")).click();
        element(by.id("awareness_contact_cards_amount")).clear().sendKeys('100');
        element(by.id("awareness_awareness_party_bool")).click();
        element(by.id("awareness_awareness_party_amount")).clear().sendKeys('200');
        element(by.id("awareness_sign_boards_bool")).click();
        element(by.id("awareness_sign_boards_amount")).clear().sendKeys('300');
        element(by.id("awareness_add_item")).click();
        //element(by.xpath("//form[@id='budget-calc-form']/div[1]/div[2]/div[3]/div[2]/div[4]/div[1]/div[1]/input")).clear().sendKeys('Test1');
        //element(by.xpath("//form[@id='budget-calc-form']/div[1]/div[2]/div[3]/div[2]/div[4]/div[1]/div[2]/input")).clear().sendKeys('100');
        element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as awarenessItemsCtrl']/div/div/input")).clear().sendKeys('Test1');
        element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as awarenessItemsCtrl']/div/div[2]/input")).clear().sendKeys('100');
        element(by.id("travel_chair_with_bike_bool")).click();
        element(by.id("travel_chair_with_bike_amount")).clear().sendKeys('100');
        element(by.id("travel_manager_with_bike_bool")).click();
        element(by.id("travel_manager_with_bike_amount")).clear().sendKeys('200');
        element(by.id("travel_number_of_staff_using_bikes")).clear().sendKeys('5');
        element(by.id("travel_number_of_staff_using_bikes_multiplier")).clear().sendKeys('10');
        element(by.id("travel_sending_girls_home_expense")).clear().sendKeys('100');
        element(by.id("travel_motorbike_bool")).click();
        element(by.id("travel_motorbike_amount")).clear().sendKeys('200');
        element(by.id("travel_other")).clear().sendKeys('300');
        element(by.id("travel_add_item")).click();
        element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as travelItemsCtrl']/div/div/input")).clear().sendKeys('Test2');
        element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as travelItemsCtrl']/div/div[2]/input")).clear().sendKeys('100');
        element(by.id("supplies_walkie_talkies_bool")).click();
        element(by.id("supplies_walkie_talkies_amount")).clear().sendKeys('100');
        element(by.id("supplies_recorders_bool")).click();
        element(by.id("supplies_recorders_amount")).clear().sendKeys('200');
        element(by.id("supplies_binoculars_bool")).click();
        element(by.id("supplies_binoculars_amount")).clear().sendKeys('300');
        element(by.id("supplies_flashlights_bool")).click();
        element(by.id("supplies_flashlights_amount")).clear().sendKeys('400');
        element(by.id("supplies_add_item")).click();
        element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as suppliesItemsCtrl']/div/div/input")).clear().sendKeys('Test3');
        element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as suppliesItemsCtrl']/div/div[2]/input")).clear().sendKeys('100');
        element(by.id("admin_number_of_interceptions_last_month")).clear().sendKeys('10');
        element(by.id("admin_number_of_interceptions_last_month_multiplier")).clear().sendKeys('20');
        element(by.id("admin_number_of_interceptions_last_month_adder")).clear().sendKeys('100');
        element(by.id("admin_number_of_meetings_per_month")).clear().sendKeys('30');
        element(by.id("admin_number_of_meetings_per_month_multiplier")).clear().sendKeys('5');
        element(by.id("admin_booth_bool")).click();
        element(by.id("admin_booth_amount")).clear().sendKeys('100');
        element(by.id("admin_registration_bool")).click();
        element(by.id("admin_registration_amount")).clear().sendKeys('200');
        element(by.id("medical_expense")).clear().sendKeys('100');
        element(by.id("misc_number_of_intercepts")).clear().sendKeys('10');
        element(by.id("misc_number_of_intercepts_mult")).clear().sendKeys('50');
        element(by.id("misc_add_item")).click();
        element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as miscItemsCtrl']/div/div/input")).clear().sendKeys('Test4');
        element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as miscItemsCtrl']/div/div[2]/input")).clear().sendKeys('100');

    };

    this.submitForm = function () {
        element(by.id("budget_create")).click();
    };

    this.updateForm = function () {
        element(by.id("budget_update")).click();
    };

    this.viewForm = function () {
        browser.get(constants.webAddress + '/budget/budget_calculations/');
        element(by.linkText("View")).click();
    };

    this.editForm = function () {
        browser.get(constants.webAddress + '/budget/budget_calculations/');
        element(by.linkText("Edit")).click();
    };

    this.navigateToForms = function () {
        browser.get(constants.webAddress + '/budget/budget_calculations/');
    };

};

module.exports = new budgetForm();