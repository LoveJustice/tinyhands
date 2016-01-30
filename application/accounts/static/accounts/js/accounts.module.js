(function() {
    'use strict';

    angular.module('AccountsMod',['ngCookies','ngAnimate', 'ngResource', 'ui.bootstrap'])
        .config(['$httpProvider','$resourceProvider', function($httpProvider, $resourceProvider) {
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
            $resourceProvider.defaults.stripTrailingSlashes = false
        }]);
})();
