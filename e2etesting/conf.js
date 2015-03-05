var constants = require('./testConstants.json');

exports.config = {
  seleniumAddress: 'http://localhost:4444/wd/hub',

  allScriptsTimeout: 10000,

  SITE_DOMAIN: '0.0.0.0:8000',

  //specs:  [
  //          'vdcs/vdcAdminPage.spec.js'
  //        ]
  specs:  ['accounts/loginPage.spec.js',
	        'irf/irfCRUD.spec.js',
            'accounts/loginPage.spec.js',
            'accounts/permissionsPage.spec.js',
            'vdcs/vdcAdminPage.spec.js',
			'dataentry/search.spec.js'
          ]

};
