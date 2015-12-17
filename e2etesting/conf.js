exports.config = {
    onPrepare: function() {
        browser.driver.manage().window().maximize();
    },

    seleniumAddress: 'http://localhost:4444/wd/hub',

    suites: {
        login: 'accounts/loginPage.spec.js',

        dataentry: ['borderStations/borderStationCRUD.spec.js',
            'dataentry/irfCRUD.spec.js',
            'dataentry/vifCrud.spec.js',
            'dataentry/search.spec.js'
        ],

        irf: 'dataentry/irfCRUD.spec.js',

        vif: 'dataentry/vifCrud.spec.js',

        border: [
            'borderStations/closeABorderStation.spec.js'
        ],

        budget: [
             'borderStations/borderStationCRUD.spec.js',
            'dataentry/irfCRUD.spec.js',
            'dataentry/vifCrud.spec.js',
            'budget/budgetForm.spec.js',
            'budget/moneyDistributionForm.spec.js'
        ],

        perm: 'accounts/permissionsPage.spec.js',

        budget_test: ['borderStations/borderStationCRUD.spec.js', 'budget/budgetForm.spec.js', 'budget/moneyDistributionForm.spec.js'],

        stations: ['accounts/loginPage.spec.js', 'borderStations/borderStationCRUD.spec.js', 'DynStationWindow/dynStation.spec.js'],

        portal: [
            'portal/tally.spec.js'
        ],

        dynstationwindow: [
            'DynStationWindow/dynStation.spec.js'
        ],

        addresses: [
            'addresses/vdcAdminPage.spec.js',
            'addresses/address1Page.spec.js'
        ]
    },

    //The order is very important. Ex. budgetForm.spec.js is dependant on borderStationCRUD.spec.js
    specs:  [
        // First logically
        'accounts/loginPage.spec.js',
        'borderStations/borderStation.spec.js',
        /////////// 'borderStations/borderStationCRUD.spec.js',
        'dataentry/irfList.spec.js',
        'dataentry/vifList.spec.js',
        'dataentry/irfCRUD.spec.js',
        'dataentry/vifCrud.spec.js',
        'dataentry/search.spec.js', //dependent on vifCrud.spec.js and irfCRUD.spec.js

        //These three are dependent on each other
        'borderStations/closeABorderStation.spec.js',
        'budget/budgetForm.spec.js',
        'budget/moneyDistributionForm.spec.js',

        'DynStationWindow/dynStation.spec.js',

        'addresses/vdcAdminPage.spec.js',
        'addresses/address1Page.spec.js',
        'accounts/accessDefaults.spec.js',

        'portal/tally.spec.js',

        //'accounts/permissionsPage.spec.js' // Has to run last
      ],

    framework: 'jasmine2',

    capabilities: {
        "browserName":"chrome"
    }
};
