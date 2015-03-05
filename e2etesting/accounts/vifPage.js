'use strict';

var constants = require('../testConstants.json');
var permissionsPage = require('./permissionsPage.js');

var vifPage = function() {
    var page = this;

    this.createVif = function(){
        browser.get(constants.webAddress + '/data-entry/vifs/create/');
    };

    this.filloutVif = function(){
          if(true) {
              browser.executeScript("arguments[0].style.visibility = 'hidden';", element(by.id("footer")).getWebElement()); // Hides the footer so the webdriver can click on stuff
              this.vif_number = element(by.id("id_vif_number")).sendKeys("BHD123");
              this.date = element(by.id("id_date")).sendKeys("02/16/2015");
              this.interviewer = element(by.id("id_interviewer")).sendKeys("Test Interviewer");
              this.statement_read_before_beginning = element(by.id("id_statement_read_before_beginning")).click();
              this.gender = element(by.id("id_victim_gender_0")).click();
              this.victim_name = element(by.id("id_victim_name")).sendKeys("Test Victim");
              this.victim_address_district = element(by.id("id_victim_address_district")).sendKeys("Baglung");
              this.victim_address_vdc = element(by.id("id_victim_address_vdc")).sendKeys("ShreeJung");
              this.victim_guardian_address_district = element(by.id("id_victim_guardian_address_district")).sendKeys("Baglung");
              this.victim_guardian_address_vdc = element(by.id("id_victim_guardian_address_vdc")).sendKeys("ShreeJung");
              this.migration_plans = element(by.id("id_migration_plans_education")).click();
              this.primary_motivation = element(by.id("id_primary_motivation_support_myself")).click();
              browser.executeScript('window.scrollTo(13,1050);');/*.then(function () {*/
              this.victim_recruited_in_village = element(by.id("id_victim_recruited_in_village_0")).click();
              //});
              this.victim_primary_means_of_travel = element(by.id("id_victim_primary_means_of_travel_tourist_bus")).click();
              this.victim_stayed_somewhere_between = element(by.id("id_victim_stayed_somewhere_between_0")).click();
              this.meeting_at_border = element(by.id("id_meeting_at_border_yes")).click();
              //browser.executeScript('window.scrollTo(644, 1050);');
              this.victim_knew_details_about_destination = element(by.id("id_victim_knew_details_about_destination_0")).click();
              //browser.executeScript('window.scrollTo(378, 1200);');
              this.awareness_before_interception = element(by.id("id_awareness_before_interception_had_heard_not_how_bad")).click();
              this.attitude_towards_tiny_hands = element(by.id("id_attitude_towards_tiny_hands_thankful")).click();
              this.victim_heard_gospel = element(by.id("id_victim_heard_gospel_no")).click();
              this.legal_action_against_traffickers = element(by.id("id_legal_action_against_traffickers_no")).click();
              this.has_signature = element(by.id("id_has_signature")).click();
              browser.executeScript("arguments[0].style.visibility = '';", element(by.id("footer")).getWebElement()); // Hides the footer so the webdriver can click on stuff
              this.submitButton = element(by.id("id_interviewer")).submit();
              this.ignore_warnings = element(by.id("id_ignore_warnings")).click();
              //browser.sleep(5000);
              this.submitButton = element(by.id("id_interviewer")).submit();
          }

    };
};

module.exports = new vifPage();