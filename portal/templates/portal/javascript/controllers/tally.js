(function() {
    'use strict';

    angular.module('PortalMod')
           .controller('TallyCtrl', TallyCtrl);

    TallyCtrl.$inject = ['$rootScope','tallyService'];

    function TallyCtrl($rootScope,tallyService) {
        var vm = this;

        vm.days = {};
        vm.changeColor = changeColor;
        vm.checkDifferences = checkDifferences;
        vm.getTallyData = getTallyData;
        vm.hasIntercepts = false;
        vm.isEmptyObject = isEmptyObject;
        vm.onMouseLeave = onMouseLeave;
        vm.showTally = true;
        vm.showVDCLayer = true;
        vm.sumNumIntercepts = sumNumIntercepts;
        vm.toggleVDCLayer = toggleVDCLayer;

        activate();

        function activate() {
            getTallyData(true);

            // Prevent dropdown from closing after click
            $('#tally .dropdown-menu').click(function(e) {
                e.stopPropagation();
            });
        }

        function changeColor(day) {
            if (day.change && !day.seen) {
                return {'background-color': 'rgba(255,0,0,0.5)',
                        'color': 'white'};
            }
        }

        function checkDifferences(data){
            for(var i = 0; i < 7; i++){
                var interceptions = data[i].interceptions;
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

        function getTallyData(firstCall) {
            return tallyService.getTallyDays().then(function(promise) {
                var data = promise.data;
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
            });
        }

        function isEmptyObject(obj) {
            return $.isEmptyObject(obj);
        }

        function onMouseLeave(day){
            day.seen = true;
        }

        function sumNumIntercepts(day) {
            var sumInt = 0;
            for (var key in day.interceptions) {
                sumInt += day.interceptions[key];
            }
            return sumInt;
        }

        function toggleVDCLayer() {
            $rootScope.$emit('toggleVDCLayer', vm.showVDCLayer);
        }
    };

})();
