// Karma configuration
// Generated on Tue Apr 21 2015 16:02:02 GMT-0400 (EDT)angular-mocks

module.exports = function(config) {
  config.set({

    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: '',


    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['jasmine', 'requirejs'],


    // list of files / patterns to load in the browser
    // !!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!
    // DO NOT CHANGE THIS VARIABLE :) -B. Sell 10/6/2015
    files: [
        'test-main.js',
        'node_modules/angular/angular.js',
        'static/jquery.js',
        'static/angular-bootstrap/ui-bootstrap-custom-0.13.4.js',
        'static/angular-bootstrap/ui-bootstrap-custom-tpls-0.13.4.js' ,
        'static/angular-ui-calendar/angular-ui-calendar.min.js',
        'node_modules/angular-cookies/angular-cookies.js',
        'node_modules/angular-animate/angular-animate.js',
        'node_modules/angular-route/angular-route.js',
        'node_modules/angular-mocks/angular-mocks.js',  
        'node_modules/angular-resource/angular-resource.js',
        '**/static/**/*.module.js',
        '**/static/**/controllers/*.js',
        '**/static/**/services/*.js',
        
        {pattern: 'karma/**/*.spec.js', included: false}
    ],

    // list of files to exclude
    exclude: [
    ],


    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
    },


    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['progress'],


    // web server port
    port: 9876,


    // enable / disable colors in the output (reporters and logs)
    colors: true,


    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,


    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,


    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['PhantomJS'],

    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: false
  });
};
