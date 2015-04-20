(function() {
    'use strict';

    angular.module('PortalMod')
           .controller('TallyCtrl', TallyCtrl);

    TallyCtrl.$inject = ['$rootScope','$http'];

    function TallyCtrl($rootScope,$http) {
        var vm = this;

        vm.days = {};
        vm.hasIntercepts = false;
        vm.showVDCLayer = true;
        vm.showTally = true;
        vm.isEmptyObject = isEmptyObject;
        vm.changeColor = changeColor;
        vm.toggleVDCLayer = toggleVDCLayer;

        activate();

        function activate() {
            getTallyData();

            // Prevent dropdown from closing after click
            $('#tally .dropdown-menu').click(function(e) {
                e.stopPropagation();
            });
        }

        function isEmptyObject(obj) {
            return $.isEmptyObject(obj);
        }

        function changeColor(day) {
            if (!$.isEmptyObject(day.interceptions)) {
                return {'background-color': 'rgba(255,0,0,0.5)',
                        'color': 'rgba(255,255,255,1)'};
            }
        }

        function toggleVDCLayer() {
            $rootScope.$emit('toggleVDCLayer', vm.showVDCLayer);
        }

        function getTallyData() {
            $http.get('/portal/tally/days/')
                .success(function(data) {
                // Data should be:
                // {0:{dayOfWeek:'Monday',
                //     interceptions: {<String of StationCode>:<Num of Interceptions>}},
                //  1:{dayOfWeek:'Sunday',
                //     interceptions: {...}},
                // }
                vm.days = data;
            })
                .error(function(error) {
                console.log(error);
            });
        }
    };
})();

angular.bootstrap($('#portal'), ['PortalMod']);
