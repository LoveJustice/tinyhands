angular
    .module('DataEntry')
    .controller("staffListCtrl", ['$scope','$http', 'staffListService', function($scope, $http, staffListService) {
        var vm = this;

        // Variable Declarations
        vm.staffNames = [];
        vm.testNames = [];
        vm.stationID;
        vm.station_code = "";

        // Function Definitions
        vm.retrieveStaff = retrieveStaff;
        vm.irfNumChange = irfNumChange;

        function retrieveStaff() {
            console.log("Retrieving");
            // grab all of the staff for this border station
            // TODO: need to get station code from form on page
            // Include watch from https://docs.angularjs.org/api/ng/type/$rootScope.Scope to $digest stationID to see if it changed
            // staffListService.retrieveStaff(formNum[:3]).then(function(promise) {
            staffListService.retrieveStaff(vm.stationID).then(function(promise){
                var data = promise.data;
                vm.staffNames=[];
                $(data).each(function(person){
                        vm.staffNames.push(
                            {
                                staff_person: data[person].id,
                                name: data[person]['first_name'] + ' ' + data[person]['last_name'],
                            }
                        );
                });
            });
        }

        $scope.$on('handleStaffNamesChangeBroadcast', function(event, args) {
                vm.staffNames = args['names'];
        });

        function irfNumChange(irf_num) {
            console.log("Got: " + irf_num);
            vm.station_code = irf_num.slice(0,3);
            console.log(vm.station_code);
            staffListService.getStationID(vm.station_code).then(function(response){
                vm.stationID = response;
            })

        }

    }]);