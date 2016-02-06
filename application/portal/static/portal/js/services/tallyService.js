(function() {
    'use strict';

    angular.module('PortalMod')
           .factory('tallyService', tallyService);

    tallyService.$inject = ['$http'];

    function tallyService($http) {
        var service = {
            getTallyDays: getTallyDays,
        };

        return service;

        function getTallyDays() {
            return $http.get('/portal/tally/days/')
                 .success(function(data) {
                    return data;
                }).error(function(error) {
                    console.log(error);
                });
        }
    }
})();
