angular
    .module('DataEntry')
    .controller("staffListCtrl", ['$scope','$http', 'staffService', function($scope, $http, staffService) {
        var vm = this;

        // Variable Declarations
        vm.staffNames = [];

        // Function Definitions
        vm.retrieveStaff = retrieveStaff;

        function retrieveStaff() {
            // grab all of the staff for this border station
            // TODO: should get border station based on form number on page
            staffService.retrieveStaff(1).then(function(promise){
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
    }]);