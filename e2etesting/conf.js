var constants = require('./testConstants.json');

exports.config = {

  seleniumAddress: 'http://localhost:4444/wd/hub',

  specs:  [
        'accounts/loginPage.spec.js',
        'accounts/permissionsPage.spec.js',
        'dataentry/irfCRUD.spec.js',
        'dataentry/search.spec.js',
        'dataentry/vifCrud.spec.js',
        'borderStations/borderStationCRUD.spec.js',
        'budget/budgetForm.spec.js',
        'vdcs/vdcAdminPage.spec.js'
      ]

};
