'use strict';

var c = require('../testConstants.json');
//var permissionsPage = require('./permissionsPage.js');

var vifPage = function() {
    var page = this;

    // define elements here - use them in tests
    this.attitude_towards_tiny_hands = element(by.id("id_attitude_towards_tiny_hands_thankful"));
    this.awareness_before_interception = element(by.id("id_awareness_before_interception_had_heard_not_how_bad"));
    this.date = element(by.id("id_date"));
    this.gender = element(by.id("id_victim_gender_0"));
    this.has_signature = element(by.id("id_has_signature"));
    this.ignore_warnings = element(by.id("id_ignore_warnings"));
    this.interviewer = element(by.id("id_interviewer"));
    this.legal_action_against_traffickers = element(by.id("id_legal_action_against_traffickers_no"));
    this.meeting_at_border = element(by.id("id_meeting_at_border_yes"));
    this.migration_plans = element(by.id("id_migration_plans_education"));
    this.primary_motivation = element(by.id("id_primary_motivation_support_myself"));
    this.statement_read_before_beginning = element(by.id("id_statement_read_before_beginning"));
    this.submitButton = element(by.id("id_interviewer"));
    this.saveForlater = element(by.id("save-for-later"));
    this.victim_address_district = element(by.id("id_victim_address_district"));
    this.victim_address_vdc = element(by.id("id_victim_address_vdc"));
    this.victim_guardian_address_district = element(by.id("id_victim_guardian_address_district"));
    this.victim_guardian_address_vdc = element(by.id("id_victim_guardian_address_vdc"));
    this.victim_heard_gospel = element(by.id("id_victim_heard_gospel_no"));
    this.victim_knew_details_about_destination = element(by.id("id_victim_knew_details_about_destination_0"));
    this.victim_name = element(by.id("id_victim_name"));
    this.victim_primary_means_of_travel = element(by.id("id_victim_primary_means_of_travel_tourist_bus"));
    this.victim_recruited_in_village = element(by.id("id_victim_recruited_in_village_0"));
    this.victim_stayed_somewhere_between = element(by.id("id_victim_stayed_somewhere_between_0"));
    this.vif_number = element(by.id("id_vif_number"));
    this.vif_number_of_victims = element(by.id("id_number_of_victims"));

    this.createVif = function(){
        browser.get(c.webAddress + '/data-entry/vifs/create/');
    };

    this.filloutVif = function(vifNumber) {
        browser.executeScript("arguments[0].style.visibility = 'hidden';", element(by.id("footer")).getWebElement()); // Hides the footer so the webdriver can click on stuff
        this.vif_number_of_victims.sendKeys("1");
        this.vif_number.sendKeys(vifNumber);
        this.date.sendKeys(c.vifDate);
        this.interviewer.sendKeys(c.vifInterviewer);
        this.statement_read_before_beginning.click();
        this.gender.click();
        this.victim_name.sendKeys(c.vifVictimName);
        this.victim_address_district.sendKeys(c.vifAddressDistrict);
        this.victim_address_vdc.sendKeys(c.vifAddressVDC);
        this.victim_guardian_address_district.sendKeys(c.vifVictimGuardianAddressDistrict);
        this.victim_guardian_address_vdc.sendKeys(c.vifVictimGuardianAddressVDC);
        this.migration_plans.click();
        this.primary_motivation.click();
        this.victim_recruited_in_village.click();
        this.victim_primary_means_of_travel.click();
        this.victim_stayed_somewhere_between.click();
        this.meeting_at_border.click();
        this.victim_knew_details_about_destination.click();
        this.awareness_before_interception.click();
        this.attitude_towards_tiny_hands.click();
        this.victim_heard_gospel.click();
        this.legal_action_against_traffickers.click();
        this.has_signature.click();
        browser.executeScript("arguments[0].style.visibility = '';", element(by.id("footer")).getWebElement()); // unhides the footer so the webdriver can click on stuff
        this.submitButton.submit();
        this.ignore_warnings.click();
        this.submitButton.submit();
    };

    this.partialfilloutVif1 = function(vifNumber) {
        browser.executeScript("arguments[0].style.visibility = 'hidden';", element(by.id("footer")).getWebElement()); // unhides the footer so the webdriver can click on stuff
        this.vif_number.sendKeys(vifNumber);
        this.date.sendKeys(c.vifDate);
        this.interviewer.sendKeys(c.vifInterviewer);
        this.statement_read_before_beginning.click();
        this.gender.click();
        //browser.pause();
        browser.executeScript("arguments[0].style.visibility = '';", element(by.id("footer")).getWebElement()); // Hides the footer so the webdriver can click on stuff
        this.saveForlater.click();
        browser.sleep(1000);
        browser.switchTo().alert().accept();
    };

    this.partialfilloutVif2 = function(vifNumber) {
        browser.executeScript("arguments[0].style.visibility = 'hidden';", element(by.id("footer")).getWebElement()); // unhides the footer so the webdriver can click on stuff
        this.vif_number.sendKeys(vifNumber);
        this.date.sendKeys(c.vifDate);
        this.migration_plans.click();
        this.primary_motivation.click();
        this.victim_recruited_in_village.click();
        this.victim_primary_means_of_travel.click();
        this.victim_stayed_somewhere_between.click();
        this.meeting_at_border.click();
        this.victim_knew_details_about_destination.click();
        this.awareness_before_interception.click();
        this.attitude_towards_tiny_hands.click();
        this.victim_heard_gospel.click();
        this.legal_action_against_traffickers.click();
        this.has_signature.click();
        //browser.pause();
        browser.executeScript("arguments[0].style.visibility = '';", element(by.id("footer")).getWebElement()); // Hides the footer so the webdriver can click on stuff
        this.saveForlater.click();
        browser.sleep(1000);
        browser.switchTo().alert().accept();
    };
};

module.exports = new vifPage();