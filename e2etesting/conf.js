var constants = require('./testConstants.json');

exports.config = {

    onPrepare: function() {
        browser.driver.manage().window().setSize(2000,1800);
    },

    seleniumAddress: 'http://localhost:4444/wd/hub',

  specs:  [
        'accounts/loginPage.spec.js',
        'irf/irfCRUD.spec.js',  //There are problems in this one
        'vdcs/vdcAdminPage.spec.js', //There are problems in this one
        'borderStations/borderStationCRUD.spec.js',
        'dataentry/vifCrud.spec.js',
        'dataentry/search.spec.js',
        'budget/budgetForm.spec.js',
        'accounts/permissionsPage.spec.js'
        'DynStationWindow/dynStation.spec.js',
      ],

    capabilities: {
        "browserName":"chrome"
    }
};
