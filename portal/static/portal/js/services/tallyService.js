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
                    // Data should be:
                    // {0:{dayOfWeek:'Monday',
                    //     interceptions: {<String of StationCode>:<Num of Interceptions>}},
                    //  1:{dayOfWeek:'Sunday',
                    //     interceptions: {...}},
                    // }
                    return data;
                }).error(function(error) {
                    console.log(error);
                });
        }
    }
})();
