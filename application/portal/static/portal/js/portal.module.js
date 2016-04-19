(function() {
    'use strict';

    angular.module('PortalMod',['ngCookies','ngAnimate','EventsMod'])
        .config(['$httpProvider', function($httpProvider) {
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        }]);
})();
