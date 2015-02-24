var constants = require('./testConstants.json');

exports.config = {
  seleniumAddress: 'http://localhost:4444/wd/hub',
  allScriptsTimeout: 10000,
  specs:  ['accounts/permissionsPage.spec.js']
  //specs:  ['accounts/loginPage.spec.js',
  //          'accounts/permissionsPage.spec.js',
  //          'vdcs/vdcAdminPage.spec.js'
  //        ]
};
