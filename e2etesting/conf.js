// conf.js
exports.config = {
  seleniumAddress: 'http://localhost:4444/wd/hub',
  specs: ['spec.js',
	  'otherspec.js', 
	  'portal/*'
	 ]
}
