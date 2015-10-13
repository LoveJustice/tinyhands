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

        'borderStations/borderStationCRUD.spec.js',

        //'dataentry/irfCRUD.spec.js',
        //'dataentry/vifCrud.spec.js',
        //'dataentry/search.spec.js',

        'budget/budgetForm.spec.js',
        'budget/moneyDistributionForm.spec.js'

        //'DynStationWindow/dynStation.spec.js',

        //'vdcs/vdcAdminPage.spec.js', //There are problems in this one

        // Has to run last
        //'accounts/permissionsPage.spec.js'
      ],

    framework: 'jasmine2',

    capabilities: {
        "browserName":"chrome"
    }
};
