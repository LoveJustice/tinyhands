angular
    .module('BudgetCalculation')
    .controller("staffCtrl", ['$scope','$http', 'staffService', function($scope, $http, staffService) {
<<<<<<< HEAD
        // get staff for a border_station http://localhost:8000/static_border_stations/api/border-stations/0/
        var vm = this;
        vm.staffSalaryForms = [];
        vm.staffTotal = 0;

        vm.totalSalaries = totalSalaries;
        vm.saveAllSalaries = saveAllSalaries;
        vm.retrieveStaff = retrieveStaff;
        vm.retrieveStaffSalaries = retrieveStaffSalaries;

        main();

        $scope.$on('handleBudgetCalcSavedBroadcast', function(event, args) {
            vm.saveAllSalaries();
        });

        function main(){
            if( window.submit_type == 1 ) {
                vm.retrieveStaff();
=======
        var vm = this;

        // Variable Declarations
        vm.staffSalaryForms = [];
        vm.staffTotal = 0;

        // Function Definitions
        vm.retrieveStaff = retrieveStaff;
        vm.retrieveStaffSalaries = retrieveStaffSalaries;
        vm.retrieveOldStaffSalaries = retrieveOldStaffSalaries;
        vm.totalSalaries = totalSalaries;
        vm.saveAllSalaries = saveAllSalaries;

        // Calling the main function
        main();

        function main(){
            if( window.submit_type == 1 ) {
                vm.retrieveStaff();
                vm.retrieveOldStaffSalaries();
>>>>>>> demo/v0.3-local
            }
            else if( window.submit_type == 2)  {
                vm.retrieveStaffSalaries();
            }
            else {
                vm.retrieveStaffSalaries();
            }
        }

<<<<<<< HEAD
=======
        // Event Listeners
        $scope.$on('handleBudgetCalcSavedBroadcast', function() {
            vm.saveAllSalaries();
        });

        // Function implementations
>>>>>>> demo/v0.3-local
        function totalSalaries(){
            var acc = 0;
            for(var x = 0; x < vm.staffSalaryForms.length; x++){
                acc += vm.staffSalaryForms[x].salary;
            }
            $scope.$emit('handleSalariesTotalChangeEmit', {total: acc});
            vm.staffTotal = acc;
        }

        function retrieveStaff() {
            // grab all of the staff for this budgetCalcSheet
            staffService.retrieveStaff(window.border_station).then(function(promise){
                var data = promise.data;
                $(data).each(function(person){
                        vm.staffSalaryForms.push(
                            {
                                staff_person: data[person].id,
                                name: data[person]['first_name'] + ' ' + data[person]['last_name'],
                                budget_calc_sheet: 0,
                                salary: 0
                            }
                        );
                });
            });
        }

        function retrieveStaffSalaries() {
            staffService.retrieveStaffSalaries()
                .then(function(promise){
                    var staffData = promise[0].data;
                    var staffSalariesData = promise[1].data;
<<<<<<< HEAD

=======
>>>>>>> demo/v0.3-local
                    for(var person = 0; person < staffSalariesData.length; person++) {
                        for (var x = 0; x < staffData.length; x++) {
                            if (staffData[x].id === staffSalariesData[person].staff_person) {
                                staffSalariesData[person].name = staffData[x].first_name + ' ' + staffData[x].last_name;
                            }
                        }
                        vm.staffSalaryForms.push(staffSalariesData[person])
                    }
                });
        }

<<<<<<< HEAD

        function saveAllSalaries(){
            for(var person = 0; person < vm.staffSalaryForms.length; person++){
                item = vm.staffSalaryForms[person];
                if(!item.id){
=======
        function retrieveOldStaffSalaries() {
            staffService.retrieveOldStaffSalaries()
                .then(function(promise){
                    var staffData = promise[0].data;
                    var staffSalariesData = promise[1].data.staff_salaries;

                    for(var person = 0; person < staffSalariesData.length; person++) {
                        for (var x = 0; x < staffData.length; x++) {
                            if (staffData[x].id === staffSalariesData[person].staff_person) {
                                staffSalariesData[person].name = staffData[x].first_name + ' ' + staffData[x].last_name;
                            }
                        }

                        var newperson = staffSalariesData[person];
                        newperson.id = undefined;
                        for(var oldPerson = 0; oldPerson < vm.staffSalaryForms.length; oldPerson++){

                            if( newperson.staff_person == vm.staffSalaryForms[oldPerson].staff_person){
                                vm.staffSalaryForms.splice(oldPerson,1);
                            }
                        }
                        vm.staffSalaryForms.push(newperson);
                    }
                });
        }


        function saveAllSalaries(){
            var item = {};
            for(var person = 0; person < vm.staffSalaryForms.length; person++){
                item = vm.staffSalaryForms[person];
                if(item.id === undefined){
>>>>>>> demo/v0.3-local
                    saveItem(item);
                }else{
                    updateItem(item);
                }
            }
        }

<<<<<<< HEAD
=======
        // Helper functions for saveAllSalaries
>>>>>>> demo/v0.3-local
        function saveItem(item){
            staffService.saveItem(item);
        }

        function updateItem(item){
            staffService.updateItem(item);
        }
    }]);