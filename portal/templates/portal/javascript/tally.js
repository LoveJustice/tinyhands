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
        vm.onMouseLeave = onMouseLeave;

        activate();

        function activate() {
            getTallyData(true);

            // Prevent dropdown from closing after click
            $('#tally .dropdown-menu').click(function(e) {
                e.stopPropagation();
            });
        }

        function isEmptyObject(obj) {
            return $.isEmptyObject(obj);
        }

        function changeColor(day) {
            if (day.change && !day.seen) {
                return {'background-color': 'rgba(255,0,0,0.5)',
                        'color': 'rgba(255,255,255,1)'};
            }
        }

        function toggleVDCLayer() {
            $rootScope.$emit('toggleVDCLayer', vm.showVDCLayer);
        }

        function onMouseLeave(day){
            day.seen = true;
        }

        function getTallyData(firstCall) {
            $http.get('/portal/tally/days/')
                .success(function(data) {
                // Data should be:
                // {0:{dayOfWeek:'Monday',
                //     interceptions: {<String of StationCode>:<Num of Interceptions>}},
                //  1:{dayOfWeek:'Sunday',
                //     interceptions: {...}},
                // }
                if(firstCall){
                    for(var i = 0; i < 7; i++){
                        data[i].change = false;
                        data[i].seen = false;
                    }
                    vm.days = data;
                    setInterval(getTallyData, 60000);
                }else{ //updates
                    checkDifferences(data);
                }
            })
                .error(function(error) {
                console.log(error);
            });
        }

        function checkDifferences(data){
            for(var i = 0; i < 7; i++){
                interceptions = data[i].interceptions;
                data[i].change = false;
                data[i].seen = false;
                for(var key in interceptions){
                    if(interceptions.hasOwnProperty(key)){
                        if(vm.days[i].interceptions[key] != interceptions[key]){
                            //data has changed
                            data[i].change = true;
                        }else if(vm.days[i].change && !vm.days[i].seen){
                            //data was previously changed but has not been seen
                            data[i].change = true;
                        }
                    }
                }
            }
            vm.days = data;
        }
    };

    angular.bootstrap($('#portal'), ['PortalMod']);
})();
