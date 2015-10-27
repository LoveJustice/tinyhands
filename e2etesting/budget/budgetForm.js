'use strict';

var c = require('../testConstants.json');
var methods = require('../commonMethods.js');

var budgetForm = function () {

    var page = this;

    this.navigateToNewForm = function () {
        browser.get(c.webAddress + '/static_border_stations/border-stations/update/24/');
        browser.sleep(1000);
        methods.click(element(by.linkText("New Budget Calculation Form")));
    };

    this.readForm = function () {
        this.testForm = {};
        this.testForm.shelter_rent = element(by.id("shelter_rent"));
        this.testForm.shelter_water =  element(by.id("shelter_water"));
        this.testForm.shelter_electricity=  element(by.id("shelter_electricity"));
        this.testForm.shelter_startup_bool=  element(by.id("shelterStartupBool"));
        this.testForm.shelter_startup_amount = element(by.id("shelter_startup_amount"));
        this.testForm.shelter_two_bool = element(by.id("shelter_two_bool"));
        this.testForm.shelter_two_amount =  element(by.id("shelter_two_amount"));
        this.testForm.food_gas_multiplier_amount = element(by.id("food_gas_multiplier_before"));
        this.testForm.food_gas_number_of_girls = element(by.id("food_gas_number_of_girls"));
        this.testForm.food_gas_multiplier_after = element(by.id("food_gas_multiplier_after"));
        this.testForm.limbo_multiplier = element(by.id("limbo_multiplier"));
        this.testForm.limbo_number_of_girls = element(by.id("limbo_number_of_girls"));
        this.testForm.limbo_number_of_days = element(by.id("limbo_number_of_days"));
        this.testForm.comm_chair_bool = element(by.id("comm_chair_bool"));
        this.testForm.comm_chair_amount = element(by.id("comm_chair_amount"));
        this.testForm.comm_manager_bool = element(by.id("comm_manager_bool"));
        this.testForm.comm_manager_amount = element(by.id("comm_manager_amount"));
        this.testForm.comm_number_of_staff_wt = element(by.id("comm_number_of_staff_wt"));
        this.testForm.comm_number_of_staff_wt_multiplier = element(by.id("comm_number_of_staff_wt_multiplier"));
        this.testForm.comm_each_staff_wt = element(by.id("comm_each_staff_wt"));
        this.testForm.comm_each_staff_wt_multiplier = element(by.id("comm_each_staff_wt_multiplier"));
        this.testForm.awareness_contact_cards_bool = element(by.id("awareness_contact_cards_bool"));
        this.testForm.awareness_contact_cards_amount = element(by.id("awareness_contact_cards_amount"));
        this.testForm.awareness_awareness_party_bool = element(by.id("awareness_awareness_party_bool"));
        this.testForm.awareness_awareness_party_amount = element(by.id("awareness_awareness_party_amount"));
        this.testForm.awareness_sign_boards_bool = element(by.id("awareness_sign_boards_bool"));
        this.testForm.awareness_sign_boards_amount = element(by.id("awareness_sign_boards_amount"));
        this.testForm.awareness_add_item = element(by.id("awareness_add_item"));
        this.testForm.awareness_extra_item_name = element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as awarenessItemsCtrl']/div/div/input"));
        this.testForm.awareness_extra_item_cost = element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as awarenessItemsCtrl']/div/div[2]/input"));
        this.testForm.travel_chair_with_bike_bool = element(by.id("travel_chair_with_bike_bool"));
        this.testForm.travel_chair_with_bike_amount = element(by.id("travel_chair_with_bike_amount"));
        this.testForm.travel_manager_with_bike_bool = element(by.id("travel_manager_with_bike_bool"));
        this.testForm.travel_manager_with_bike_amount = element(by.id("travel_manager_with_bike_amount"));
        this.testForm.travel_number_of_staff_using_bikes = element(by.id("travel_number_of_staff_using_bikes"));
        this.testForm.travel_number_of_staff_using_bikes_multiplier = element(by.id("travel_number_of_staff_using_bikes_multiplier"));
        this.testForm.travel_sending_girls_home_expense = element(by.id("travel_sending_girls_home_expense"));
        this.testForm.travel_motorbike_bool = element(by.id("travel_motorbike_bool"));
        this.testForm.travel_motorbike_amount = element(by.id("travel_motorbike_amount"));
        this.testForm.travel_other = element(by.id("travel_other"));
        this.testForm.travel_add_item = element(by.id("travel_add_item"));
        this.testForm.travel_extra_item_name = element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as travelItemsCtrl']/div/div/input"));
        this.testForm.travel_extra_item_cost = element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as travelItemsCtrl']/div/div[2]/input"));
        this.testForm.supplies_walkie_talkies_bool = element(by.id("supplies_walkie_talkies_bool"));
        this.testForm.supplies_walkie_talkies_amount = element(by.id("supplies_walkie_talkies_amount"));
        this.testForm.supplies_recorders_bool = element(by.id("supplies_recorders_bool"));
        this.testForm.supplies_recorders_amount = element(by.id("supplies_recorders_amount"));
        this.testForm.supplies_binoculars_bool = element(by.id("supplies_binoculars_bool"));
        this.testForm.supplies_binoculars_amount = element(by.id("supplies_binoculars_amount"));
        this.testForm.supplies_flashlights_bool = element(by.id("supplies_flashlights_bool"));
        this.testForm.supplies_flashlights_amount = element(by.id("supplies_flashlights_amount"));
        this.testForm.supplies_add_item = element(by.id("supplies_add_item"));
        this.testForm.supplies_extra_item_name = element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as suppliesItemsCtrl']/div/div/input"));
        this.testForm.supplies_extra_item_cost = element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as suppliesItemsCtrl']/div/div[2]/input"));
        this.testForm.admin_number_of_interceptions_last_month = element(by.id("admin_number_of_interceptions_last_month"));
        this.testForm.admin_number_of_interceptions_last_month_multiplier = element(by.id("admin_number_of_interceptions_last_month_multiplier"));
        this.testForm.admin_number_of_interceptions_last_month_adder = element(by.id("admin_number_of_interceptions_last_month_adder"));
        this.testForm.admin_number_of_meetings_per_month = element(by.id("admin_number_of_meetings_per_month"));
        this.testForm.admin_number_of_meetings_per_month_multiplier = element(by.id("admin_number_of_meetings_per_month_multiplier"));
        this.testForm.admin_booth_bool = element(by.id("admin_booth_bool"));
        this.testForm.admin_booth_amount = element(by.id("admin_booth_amount"));
        this.testForm.admin_registration_bool = element(by.id("admin_registration_bool"));
        this.testForm.admin_registration_amount = element(by.id("admin_registration_amount"));
        this.testForm.medical_expense = element(by.id("medical_expense"));
        this.testForm.misc_number_of_intercepts = element(by.id("misc_number_of_intercepts"));
        this.testForm.misc_number_of_intercepts_mult = element(by.id("misc_number_of_intercepts_mult"));
        this.testForm.misc_add_item = element(by.id("misc_add_item"));
        this.testForm.misc_extra_item_name = element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as miscItemsCtrl']/div/div/input"));
        this.testForm.misc_extra_item_cost = element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as miscItemsCtrl']/div/div[2]/input"));
    };

    this.readNewForm = function () {
        this.testNewForm = {};
        this.testNewForm.shelter_rent = element(by.id("shelter_rent"));
        this.testNewForm.shelter_water =  element(by.id("shelter_water"));
        this.testNewForm.shelter_electricity=  element(by.id("shelter_electricity"));
        this.testNewForm.shelter_startup_bool=  element(by.id("shelterStartupBool"));
        this.testNewForm.shelter_startup_amount = element(by.id("shelter_startup_amount"));
        this.testNewForm.shelter_two_bool = element(by.id("shelter_two_bool"));
        this.testNewForm.shelter_two_amount =  element(by.id("shelter_two_amount"));
        this.testNewForm.food_gas_multiplier_amount = element(by.id("food_gas_multiplier_before"));
        this.testNewForm.food_gas_number_of_girls = element(by.id("food_gas_number_of_girls"));
        this.testNewForm.food_gas_multiplier_after = element(by.id("food_gas_multiplier_after"));
        this.testNewForm.limbo_multiplier = element(by.id("limbo_multiplier"));
        this.testNewForm.limbo_number_of_girls = element(by.id("limbo_number_of_girls"));
        this.testNewForm.limbo_number_of_days = element(by.id("limbo_number_of_days"));
        this.testNewForm.comm_chair_bool = element(by.id("comm_chair_bool"));
        this.testNewForm.comm_chair_amount = element(by.id("comm_chair_amount"));
        this.testNewForm.comm_manager_bool = element(by.id("comm_manager_bool"));
        this.testNewForm.comm_manager_amount = element(by.id("comm_manager_amount"));
        this.testNewForm.comm_number_of_staff_wt = element(by.id("comm_number_of_staff_wt"));
        this.testNewForm.comm_number_of_staff_wt_multiplier = element(by.id("comm_number_of_staff_wt_multiplier"));
        this.testNewForm.comm_each_staff_wt = element(by.id("comm_each_staff_wt"));
        this.testNewForm.comm_each_staff_wt_multiplier = element(by.id("comm_each_staff_wt_multiplier"));
        this.testNewForm.awareness_contact_cards_bool = element(by.id("awareness_contact_cards_bool"));
        this.testNewForm.awareness_contact_cards_amount = element(by.id("awareness_contact_cards_amount"));
        this.testNewForm.awareness_awareness_party_bool = element(by.id("awareness_awareness_party_bool"));
        this.testNewForm.awareness_awareness_party_amount = element(by.id("awareness_awareness_party_amount"));
        this.testNewForm.awareness_sign_boards_bool = element(by.id("awareness_sign_boards_bool"));
        this.testNewForm.awareness_sign_boards_amount = element(by.id("awareness_sign_boards_amount"));
        this.testNewForm.awareness_add_item = element(by.id("awareness_add_item"));
        this.testNewForm.awareness_extra_item_name = element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as awarenessItemsCtrl']/div/div/input"));
        this.testNewForm.awareness_extra_item_cost = element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as awarenessItemsCtrl']/div/div[2]/input"));
        this.testNewForm.travel_chair_with_bike_bool = element(by.id("travel_chair_with_bike_bool"));
        this.testNewForm.travel_chair_with_bike_amount = element(by.id("travel_chair_with_bike_amount"));
        this.testNewForm.travel_manager_with_bike_bool = element(by.id("travel_manager_with_bike_bool"));
        this.testNewForm.travel_manager_with_bike_amount = element(by.id("travel_manager_with_bike_amount"));
        this.testNewForm.travel_number_of_staff_using_bikes = element(by.id("travel_number_of_staff_using_bikes"));
        this.testNewForm.travel_number_of_staff_using_bikes_multiplier = element(by.id("travel_number_of_staff_using_bikes_multiplier"));
        this.testNewForm.travel_sending_girls_home_expense = element(by.id("travel_sending_girls_home_expense"));
        this.testNewForm.travel_motorbike_bool = element(by.id("travel_motorbike_bool"));
        this.testNewForm.travel_motorbike_amount = element(by.id("travel_motorbike_amount"));
        this.testNewForm.travel_other = element(by.id("travel_other"));
        this.testNewForm.travel_add_item = element(by.id("travel_add_item"));
        this.testNewForm.travel_extra_item_name = element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as travelItemsCtrl']/div/div/input"));
        this.testNewForm.travel_extra_item_cost = element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as travelItemsCtrl']/div/div[2]/input"));
        this.testNewForm.supplies_walkie_talkies_bool = element(by.id("supplies_walkie_talkies_bool"));
        this.testNewForm.supplies_walkie_talkies_amount = element(by.id("supplies_walkie_talkies_amount"));
        this.testNewForm.supplies_recorders_bool = element(by.id("supplies_recorders_bool"));
        this.testNewForm.supplies_recorders_amount = element(by.id("supplies_recorders_amount"));
        this.testNewForm.supplies_binoculars_bool = element(by.id("supplies_binoculars_bool"));
        this.testNewForm.supplies_binoculars_amount = element(by.id("supplies_binoculars_amount"));
        this.testNewForm.supplies_flashlights_bool = element(by.id("supplies_flashlights_bool"));
        this.testNewForm.supplies_flashlights_amount = element(by.id("supplies_flashlights_amount"));
        this.testNewForm.supplies_add_item = element(by.id("supplies_add_item"));
        this.testNewForm.supplies_extra_item_name = element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as suppliesItemsCtrl']/div/div/input"));
        this.testNewForm.supplies_extra_item_cost = element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as suppliesItemsCtrl']/div/div[2]/input"));
        this.testNewForm.admin_number_of_interceptions_last_month = element(by.id("admin_number_of_interceptions_last_month"));
        this.testNewForm.admin_number_of_interceptions_last_month_multiplier = element(by.id("admin_number_of_interceptions_last_month_multiplier"));
        this.testNewForm.admin_number_of_interceptions_last_month_adder = element(by.id("admin_number_of_interceptions_last_month_adder"));
        this.testNewForm.admin_number_of_meetings_per_month = element(by.id("admin_number_of_meetings_per_month"));
        this.testNewForm.admin_number_of_meetings_per_month_multiplier = element(by.id("admin_number_of_meetings_per_month_multiplier"));
        this.testNewForm.admin_booth_bool = element(by.id("admin_booth_bool"));
        this.testNewForm.admin_booth_amount = element(by.id("admin_booth_amount"));
        this.testNewForm.admin_registration_bool = element(by.id("admin_registration_bool"));
        this.testNewForm.admin_registration_amount = element(by.id("admin_registration_amount"));
        this.testNewForm.medical_expense = element(by.id("medical_expense"));
        this.testNewForm.misc_number_of_intercepts = element(by.id("misc_number_of_intercepts"));
        this.testNewForm.misc_number_of_intercepts_mult = element(by.id("misc_number_of_intercepts_mult"));
        this.testNewForm.misc_add_item = element(by.id("misc_add_item"));
        this.testNewForm.misc_extra_item_name = element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as miscItemsCtrl']/div/div/input"));
        this.testNewForm.misc_extra_item_cost = element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as miscItemsCtrl']/div/div[2]/input"));
    };


    this.fillOutForm = function () {
        browser.sleep(500);
        browser.executeScript('document.getElementById("month_year").value = "2015-07"' );
        browser.executeScript('$("#month_year").trigger("change");');
        browser.sleep(500);
        browser.sleep(500);
        element(by.model("form.salary")).clear().sendKeys('100');
        
        element(by.id("staff_add_item")).click();
        browser.sleep(500);
        element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as staffItemsCtrl']/div/div/input")).clear().sendKeys('Staff1');
        element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as staffItemsCtrl']/div/div[2]/input")).clear().sendKeys('100');



        element(by.id("shelter_rent")).clear().sendKeys('100');
        element(by.id("shelter_water")).clear().sendKeys('200');
        element(by.id("shelter_electricity")).clear().sendKeys('300');
        element(by.id("shelterStartupBool")).click();
        element(by.id("shelter_startup_amount")).clear().sendKeys('100');
        element(by.id("shelter_two_bool")).click();
        element(by.id("shelter_two_amount")).clear().sendKeys('200');
        element(by.id("shelter_add_item")).click();

        element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as shelterItemsCtrl']/div/div/input")).clear().sendKeys('Test1');
        element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as shelterItemsCtrl']/div/div[2]/input")).clear().sendKeys('100');
        element(by.id("food_gas_multiplier_before")).clear().sendKeys('100');
        element(by.id("food_gas_number_of_girls")).clear().sendKeys('4');
        element(by.id("food_gas_multiplier_after")).clear().sendKeys('2');
        element(by.id("limbo_multiplier")).clear().sendKeys('200');
        element(by.id("limbo_number_of_girls")).clear().sendKeys('2');
        element(by.id("limbo_number_of_days")).clear().sendKeys('3');
        element(by.id("foodGas_add_item")).click();

        element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as foodGasItemsCtrl']/div/div/input")).clear().sendKeys('Test1');
        element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as foodGasItemsCtrl']/div/div[2]/input")).clear().sendKeys('100');
        element(by.id("comm_chair_bool")).click();
        element(by.id("comm_chair_amount")).clear().sendKeys('100');
        element(by.id("comm_manager_bool")).click();
        element(by.id("comm_manager_amount")).clear().sendKeys('200');
        element(by.id("comm_number_of_staff_wt")).clear().sendKeys('5');
        element(by.id("comm_number_of_staff_wt_multiplier")).clear().sendKeys('20');
        element(by.id("comm_each_staff_wt")).clear();
        element(by.id("comm_each_staff_wt")).sendKeys('100');
        element(by.id("comm_each_staff_wt_multiplier")).clear().sendKeys('5');
        element(by.id("communication_add_item")).click();

        element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as communicationItemsCtrl']/div/div/input")).clear().sendKeys('Test1');
        element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as communicationItemsCtrl']/div/div[2]/input")).clear().sendKeys('100');
        element(by.id("awareness_contact_cards_bool")).click();
        element(by.id("awareness_contact_cards_amount")).clear().sendKeys('100');
        element(by.id("awareness_awareness_party_bool")).click();
        element(by.id("awareness_awareness_party_amount")).clear().sendKeys('200');
        element(by.id("awareness_sign_boards_bool")).click();
        element(by.id("awareness_sign_boards_amount")).clear().sendKeys('300');
        element(by.id("awareness_add_item")).click();

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
        browser.sleep(2000);
        element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as miscItemsCtrl']/div/div/input")).clear().sendKeys('Test4');
        element(by.xpath("//div[@ng-controller='otherBudgetItemsCtrl as miscItemsCtrl']/div/div[2]/input")).clear().sendKeys('100');
        browser.sleep(3000);
        //browser.pause();
    };

    this.submitForm = function () {
        methods.click(element(by.id("budget_create")));
    };

    this.updateForm = function () {
        methods.click(element(by.id("budget_update")));
    };

    this.viewForm = function () {
        browser.get(c.webAddress + '/budget/api/budget_calculations/view/1/');
    };

    this.editForm = function () {
        browser.get(c.webAddress + '/budget/api/budget_calculations/update/1/');
        browser.sleep(1000);
    };

    this.navigateToForms = function () {
        browser.get(c.webAddress + '/budget/budget_calculations/');
    };

};

module.exports = new budgetForm();