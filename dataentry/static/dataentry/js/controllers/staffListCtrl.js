angular
    .module('DataEntry')
    .controller("staffListCtrl", ['$scope','$http', 'staffListService', function($scope, $http, staffListService) {
        var vm = this;

        // Variable Declarations
        vm.staffNames = [];
        vm.stationID = 5;

        // Function Definitions
        vm.retrieveStaff = retrieveStaff;

        function retrieveStaff(num) {
            console.log(num);
            // grab all of the staff for this border station
            // TODO: need to get station code from form on page
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

        function getStationID (stationCode) {
        }

        $scope.irfNumChange = function() {
            console.log("Number has changed");
        }

        function addStaffNames(formNum) {
            console.log("I got called");
            console.log(formNum);
            console.log(vm.staffNames);
            vm.staffNames = []

            vm.staffNames.push("Emily");
            vm.staffNames.push("Jon");
            vm.staffNames.push("Jenna");
            $scope.$emit('handleStaffNamesChangeEmit', {names: vm.staffNames});

        }
    }]);