var constants = require('./testConstants.json');

exports.config = {

    onPrepare: function() {
        browser.driver.manage().window().setSize(2000,1800);
    },

    seleniumAddress: 'http://localhost:4444/wd/hub',

    //The order is very important. Ex. budgetForm.spec.js is dependant on borderStationCRUD.spec.js
    specs:  [
        // First logically
        'accounts/loginPage.spec.js',
        'borderStations/borderStation.spec.js',
        //Delete the CRUD and uncomment the rest after the new borderStation testing is working
        // 'borderStations/borderStationCRUD.spec.js',

        'dataentry/irfCRUD.spec.js',
        'dataentry/vifCrud.spec.js',
        //'dataentry/search.spec.js',

        'budget/budgetForm.spec.js',
        'budget/moneyDistributionForm.spec.js',

        //'DynStationWindow/dynStation.spec.js',

        //'addresses/vdcAdminPage.spec.js', //There are problems in this one

        //'addresses/address1Page.spec.js',
        //'accounts/accessDefaults.spec.js',
        //Has to run last
        //'accounts/permissionsPage.spec.js'
      ],

    framework: 'jasmine2',

    capabilities: {
        "browserName":"chrome"
    }
};
