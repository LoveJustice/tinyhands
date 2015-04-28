var constants = require('./testConstants.json');

exports.config = {

  seleniumAddress: 'http://localhost:4444/wd/hub',

  specs:  ['accounts/loginPage.spec.js',
            'irf/irfCRUD.spec.js',
            'accounts/loginPage.spec.js',
            'vdcs/vdcAdminPage.spec.js',
            'borderStations/borderStationCRUD.spec.js',
            'dataentry/vifCrud.spec.js',
            'dataentry/search.spec.js',
            'accounts/budgetForm.spec.js',
            'accounts/permissionsPage.spec.js'
          ]

};
