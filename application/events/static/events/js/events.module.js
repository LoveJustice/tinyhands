(function() {
	'use strict';

	angular.module('EventsMod',['ngCookies','ngAnimate'])
        .config(['$httpProvider', function($httpProvider) {
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        }]);
})();
