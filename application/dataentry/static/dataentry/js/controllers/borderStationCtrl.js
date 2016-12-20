angular
    .module('DataEntry')
    .controller("borderStationCtrl", ['$scope','$http', 'borderStationService', function($scope, $http, borderStationService) {
        var vm = this;

        // Variable Declarations
        vm.staffNames = [];
        vm.testNames = [];

        // Function Definitions
        vm.retrieveStation = retrieveStation;
        vm.retrieveStaff = retrieveStaff;

        function retrieveStation(calledBy) {
            var station_code = "";
            if (calledBy == 1)
                station_code = document.getElementById("id_irf_number").value.slice(0,3);
            else
                station_code = document.getElementById("id_vif_number").value.slice(0,3);
            borderStationService.getStationID(station_code).then(function(response){
                retrieveStaff(response);
            });
        }

        function retrieveStaff(stationID) {
            if (stationID >= 0) {
                borderStationService.retrieveStaff(stationID).then(function(promise){
                    var data = promise.data;
                    vm.staffNames=[];
                    $(data).each(function(person){
                            vm.staffNames.push(
                                {
                                    staff_person: data[person].id,
                                    name: data[person]['first_name'] + ' ' + data[person]['last_name']
                                }
                            );
                    });
                });
            }
            else vm.staffNames = [{name: "Invalid Station Code"}];
        }

        $scope.$on('handleStaffNamesChangeBroadcast', function(event, args) {
                vm.staffNames = args['names'];
        });
    }]);
