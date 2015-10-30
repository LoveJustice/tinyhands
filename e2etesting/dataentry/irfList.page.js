'use strict';

var c = require('../testConstants.json');

var irfListPage = function() {
    var page = this;

    // Declare elements here, use later if needed in functions
    this.newIrfButton = element(by.id("id_input_new_irf"));
    this.exportButton = element(by.id("export"));
    this.loadMoreButton = element(by.id("vm.loadMoreButton"));
    this.searchInput = element(by.model("vm.searchValue"));
    this.paginateDropdown = element(by.model("vm.paginateBy"));

    // table headers
    this.irfNumberHeader = element(by.id("irf_number"));
    this.staffNameHeader = element(by.id("staff_name"));
    this.numberOfVictimsHeader = element(by.id("number_of_victims"));
    this.numberOfTraffickersHeader = element(by.id("number_of_traffickers"));
    this.dateTimeOfInterceptionHeader = element(by.id("date_time_of_interception"));
    this.dateTimeEnteredIntoSystemHeader = element(by.id("date_time_entered_into_system"));
    this.dateTimeLastUpdatedHeader = element(by.id("date_time_last_updated"));
    // table headers VIF
    //this.vifNumberHeader = element(by.id("vif_number"));
    //this.interviewerHeader = element(by.id("interviewer"));
    //this.numberOfVictimsHeader = element(by.id("number_of_victims"));
    //this.numberOfTraffickersHeader = element(by.id("number_of_traffickers"));
    //this.dateHeader = element(by.id("date"));
    //this.dateTimeEnteredIntoSystemHeader = element(by.id("date_time_entered_into_system"));
    //this.dateTimeLastUpdatedHeader = element(by.id("date_time_last_updated"));

    // table elements
    this.staffName = element(by.binding("irf.staff_name"));
    this.numberOfVictims = element(by.binding("irf.number_of_victims"));
    this.numberOfTraffickers = element(by.binding("irf.number_of_traffickers"));
    this.dateTimeOfInterception = element(by.binding("irf.date_time_of_interception"));
    this.dateTimeEnteredIntoSystem = element(by.binding("irf.date_time_entered_into_system"));
    this.dateTimeLastUpdated = element(by.binding("irf.date_time_last_updated"));



    this.search = function(searchValue){
        this.searchInput.sendKeys(searchValue);
        this.searchInput.submit();
    };

    this.loadMoreAddresses = function(){
        this.loadMoreButton.click();
    };
};

module.exports = irfListPage;

