var myModule = angular.module('BudgetCalculation', ['ngCookies', 'ngRoute', 'ngAnimate'])
        .config(['$httpProvider', '$routeProvider', function($httpProvider, $routeProvider) {
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        }]);



myModule.run(function($rootScope) {
    /*
        Receive emitted message and broadcast it.
        Event names must be distinct or browser will blow up!
    */

    $rootScope.$on('handleBudgetCalcSavedEmit', function(event, args) {
        $rootScope.$broadcast('handleBudgetCalcSavedBroadcast', args);
    });

    $rootScope.$on('handleOtherItemsTotalChangeEmit', function(event, args) {
        $rootScope.$broadcast('handleOtherItemsTotalChangeBroadcast', args);
    });

    $rootScope.$on('handleSalariesTotalChangeEmit', function(event, args) {
        $rootScope.$broadcast('handleSalariesTotalChangeBroadcast', args);
    });

    $rootScope.$on('lastBudgetTotalEmit', function(event, args) {
        $rootScope.$broadcast('lastBudgetTotalBroadcast', args);
    });

    $rootScope.$on('dateSetEmit', function(event, args) {
        $rootScope.$broadcast('dateSetBroadcast', args);
    });

});