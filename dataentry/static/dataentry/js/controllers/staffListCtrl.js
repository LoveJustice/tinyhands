angular
    .module('DataEntry')
    .controller("staffListCtrl", ['$scope','$http', 'staffListService', function($scope, $http, staffListService) {
        var vm = this;

        // Variable Declarations
        vm.staffNames = ["Austin","James","Munn"];

        // Function Definitions
        vm.retrieveStaff = retrieveStaff;

        function retrieveStaff() {
            // grab all of the staff for this border station
            // TODO: should get border station based on form number on page
            // var stationID = getStationID("DNG")
            // staffListService.retrieveStaff(stationID).then(function(promise) {
            staffListService.retrieveStaff(1).then(function(promise){
                var data = promise.data;
                $(data).each(function(person){
                        vm.staffNames.push(
                            {
                                staff_person: data[person].id,
                                name: data[person]['first_name'] + ' ' + data[person]['last_name'],
                            }
                        );
                });
            });
            $("input.inputResults").val("Changed it");
        }

        $scope.$on('handleStaffNamesChangeBroadcast', function(event, args) {
                vm.staffNames = args['names'];
        });

        function getStationID (stationCode) {
        }

        function addStaffNames() {
            console.log("I got called")
            console.log(vm.staffNames)
            vm.staffNames.push("Emily");
            $scope.$emit('handleStaffNamesChangeEmit', {names: staffNames});

        }
    }]);