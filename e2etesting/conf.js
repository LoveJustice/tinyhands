var constants = require('./testConstants.json');

exports.config = {

  seleniumAddress: 'http://localhost:4444/wd/hub',

  specs:  [
        //'dataentry/irfCRUD.spec.js',
        //'accounts/loginPage.spec.js',
        'borderStations/borderStationCRUD.spec.js',
        //'dataentry/vifCrud.spec.js',
        //'dataentry/search.spec.js',
        'budget/budgetForm.spec.js',
        'budget/moneyDistributionForm.spec.js'
        //'vdcs/vdcAdminPage.spec.js',
        //'accounts/permissionsPage.spec.js'
      ]

};
