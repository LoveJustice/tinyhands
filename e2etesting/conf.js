var constants = require('./testConstants.json');

exports.config = {
  seleniumAddress: 'http://localhost:4444/wd/hub',
  allScriptsTimeout: 10000,

  SITE_DOMAIN: '0.0.0.0:8000',
  capabilities: {
    'browserName': 'firefox' // or 'safari'
  },
  specs:  ['accounts/loginPage.spec.js',
	  'irf/irfCRUD.spec.js'
	  ]
};
