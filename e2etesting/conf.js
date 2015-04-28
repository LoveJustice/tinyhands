var constants = require('./testConstants.json');

exports.config = {

  seleniumAddress: 'http://localhost:4444/wd/hub',

  specs:  [
        //'irf/irfCRUD.spec.js',  //There are problems in this one
        //'vdcs/vdcAdminPage.spec.js' //There are problems in this one


        //'accounts/loginPage.spec.js',
        //'accounts/loginPage.spec.js',

        //'borderStations/borderStationCRUD.spec.js',
        //'dataentry/vifCrud.spec.js',
        //'dataentry/search.spec.js',
        'budget/budgetForm.spec.js',
        //'accounts/permissionsPage.spec.js'
      ]

};
