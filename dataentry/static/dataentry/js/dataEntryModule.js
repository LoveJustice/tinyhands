var myModule = angular.module('DataEntry', ['ngCookies', 'ngRoute', 'ngAnimate'])
        .config(['$httpProvider', '$routeProvider', function($httpProvider, $routeProvider) {
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        }]);

myModule.run(function($rootScope) {

});
