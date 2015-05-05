var loginPage = require('../accounts/loginPage.js');
var filloutform = require('../accounts/vifPage.js');
var c = require('../testConstants.json');

var vifCrud = function() {
    var page = this;

    this.navigateToCreatePage = function(){
        loginPage.loginAsAdmin();
        filloutform.createVif();
    };

    this.completeVif = function(){
        filloutform.filloutVif();
    };

    this.editVif = function() {
        this.edit = element(by.id("id_edit_vif_button")).click();
        this.clear_vif_number = element(by.id("id_vif_number")).clear();
        this.change_vif_number = element(by.id("id_vif_number")).sendKeys(c.vifNumber);
        this.hit_submit = element(by.id("id_interviewer")).submit();
        this.ignore_warnings = element(by.id("id_ignore_warnings")).click();
        this.submitButton = element(by.id("id_interviewer")).submit();
    };

    this.checkEditedVif = function() {
        this.view_edited_vif = element(by.id("id_view_vif_button")).click();
    };

    this.incorrectly_edit_vif = function() {
        this.edit = element(by.id("id_edit_vif_button")).click();
        this.clear_gender_field = element(by.id("id_migration_plans_education")).click();
        this.submitButton = element(by.id("id_interviewer")).submit();
        //this.ignore_warnings = element(by.id("id_ignore_warnings")).click();
        //this.submitButton = element(by.id("id_interviewer")).submit();

    };

    this.incorrectly_filled_out = function() {
        //Uses John's function to correctly fill out a VIF with the part which fills in the gender commented out
        if(true) {
              this.vif_number = element(by.id("id_vif_number")).sendKeys(c.vifNumber);
              this.date = element(by.id("id_date")).sendKeys("02/16/2015");
              this.interviewer = element(by.id("id_interviewer")).sendKeys("Test Interviewer");
              this.statement_read_before_beginning = element(by.id("id_statement_read_before_beginning")).click();
              //this.gender = element(by.id("id_victim_gender_0")).click();
              //browser.sleep(6000);
              this.victim_name = element(by.id("id_victim_name")).sendKeys("Test Victim");
              this.victim_address_district = element(by.id("id_victim_address_district")).sendKeys("Baglung");
              this.victim_address_vdc = element(by.id("id_victim_address_vdc")).sendKeys("Babala");
              this.victim_guardian_address_district = element(by.id("id_victim_guardian_address_district")).sendKeys("Baglung");
              this.victim_guardian_address_vdc = element(by.id("id_victim_guardian_address_vdc")).sendKeys("Babala");
              this.migration_plans = element(by.id("id_migration_plans_education")).click();
              this.primary_motivation = element(by.id("id_primary_motivation_support_myself")).click();
              this.victim_recruited_in_village = element(by.id("id_victim_recruited_in_village_0")).click();
              this.victim_primary_means_of_travel = element(by.id("id_victim_primary_means_of_travel_tourist_bus")).click();
              this.victim_stayed_somewhere_between = element(by.id("id_victim_stayed_somewhere_between_0")).click();
              this.meeting_at_border = element(by.id("id_meeting_at_border_yes")).click();
              this.victim_knew_details_about_destination = element(by.id("id_victim_knew_details_about_destination_0")).click();
              this.awareness_before_interception = element(by.id("id_awareness_before_interception_had_heard_not_how_bad")).click();
              this.attitude_towards_tiny_hands = element(by.id("id_attitude_towards_tiny_hands_thankful")).click();
              this.victim_heard_gospel = element(by.id("id_victim_heard_gospel_no")).click();
              this.legal_action_against_traffickers = element(by.id("id_legal_action_against_traffickers_no")).click();
              this.has_signature = element(by.id("id_has_signature")).click();
              this.submitButton = element(by.id("id_interviewer")).submit();
              //this.ignore_warnings = element(by.id("id_ignore_warnings")).click();
              //this.submitButton = element(by.id("id_interviewer")).submit();
          }
    };

};

module.exports = new vifCrud();