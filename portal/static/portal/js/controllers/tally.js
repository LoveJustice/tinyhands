(function() {
    'use strict';

    angular.module('PortalMod')
           .controller('TallyCtrl', TallyCtrl);

    TallyCtrl.$inject = ['$rootScope','tallyService'];

    function TallyCtrl($rootScope,tallyService) {
        var vm = this;

        var daysOfWeek = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];

        vm.days = [];
        vm.changeColor = changeColor;
        vm.checkDifferences = checkDifferences;
        vm.getDayOfWeek = getDayOfWeek;
        vm.getTallyData = getTallyData;
        vm.hasIntercepts = false;
        vm.isEmptyObject = isEmptyObject;
        vm.onMouseLeave = onMouseLeave;
        vm.getTallyLocalStorage = getTallyLocalStorage;
        vm.saveTallyLocalStorage = saveTallyLocalStorage;
        vm.showEvents = true;
        vm.showTally = true;
        vm.showVDCLayer = true;
        vm.sumNumIntercepts = sumNumIntercepts;
        vm.toggleVDCLayer = toggleVDCLayer;
        vm.userId = null;

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
            if (vm.days.length > 0) {
                for(var i in data.reverse()){
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
            }else{ //localStorage days is null
                for(var i in data){
                    if(!isEmptyObject(data[i].interceptions)){
                        data[i].change = true;
                        data[i].seen = false;
                    }
                }
            }
            vm.days = data;

        }

        function getDayOfWeek(date) {
            var newDate = moment(date);
            var today = moment().tz("Asia/Kathmandu")
            if (today.date() === newDate.date()) return 'Today';
            var nameOfDay = newDate.format('dddd');
            return nameOfDay;
        }

        function getTallyData(firstCall) {
            return tallyService.getTallyDays().then(function(promise) {
                var data = promise.data;
                if(firstCall){
                    getTallyLocalStorage();
                    checkDifferences(data.days);
                    setInterval(getTallyData, 60000);
                }else{ //updates
                    checkDifferences(data.days);
                }
                saveTallyLocalStorage();
            });
        }

        function getTallyLocalStorage() {
            var oldTally = localStorage.getItem('tally-'+vm.userId);
            if(oldTally){
                vm.days = JSON.parse(oldTally);
            }
        }

        function isEmptyObject(obj) {
            return $.isEmptyObject(obj);
        }

        function onMouseLeave(day){
            day.seen = true;
            saveTallyLocalStorage();
        }

        function saveTallyLocalStorage() {
            localStorage.setItem('tally-'+vm.userId, JSON.stringify(vm.days));
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
