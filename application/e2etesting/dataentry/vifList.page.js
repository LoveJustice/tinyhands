'use strict';

var c = require('../testConstants.json');

var vifListPage = function() {
    var page = this;

    // Declare elements here, use later if needed in functions
    this.newvifButton = element(by.id("id_input_new_vif"));
    this.exportButton = element(by.id("export"));
    this.loadMoreButton = element(by.id("vm.loadMoreButton"));
    this.searchInput = element(by.model("vm.searchValue"));
    this.paginateDropdown = element(by.model("vm.paginateBy"));

    //table headers VIF
    this.vifNumberHeader = element(by.id("vif_number"));
    this.interviewerHeader = element(by.id("interviewer"));
    this.numberOfVictimsHeader = element(by.id("number_of_victims"));
    this.numberOfTraffickersHeader = element(by.id("number_of_traffickers"));
    this.dateHeader = element(by.id("date"));
    this.dateTimeEnteredIntoSystemHeader = element(by.id("date_time_entered_into_system"));
    this.dateTimeLastUpdatedHeader = element(by.id("date_time_last_updated"));

    // table elements
    this.interviewer = element(by.binding("vif.interviewer"));
    this.number_of_victims = element(by.binding("vif.number_of_victims"));
    this.number_of_traffickers = element(by.binding("vif.number_of_traffickers"));
    this.date_time_of_interception = element(by.binding("vif.date_time_of_interception"));
    this.date_time_entered_into_system = element(by.binding("vif.date_time_entered_into_system"));
    this.date_time_last_updated = element(by.binding("vif.date_time_last_updated"));



    this.search = function(searchValue){
        this.searchInput.sendKeys(searchValue);
        this.searchInput.submit();
    };

    this.loadMoreAddresses = function(){
        this.loadMoreButton.click();
    };
};

module.exports = vifListPage;

