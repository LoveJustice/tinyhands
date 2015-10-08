var myModule = angular.module('DataEntry', ['ngCookies', 'ngRoute', 'ngAnimate','ui.bootstrap'])
        .config(['$httpProvider', '$routeProvider', function($httpProvider, $routeProvider) {
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        }]);

myModule.run(function($rootScope) {
    $rootScope.$on('handleStaffNamesChangeEmit', function(event, args) {
        $rootScope.$broadcast('handleStaffNamesChangeBroadcast', args);
    });

});
