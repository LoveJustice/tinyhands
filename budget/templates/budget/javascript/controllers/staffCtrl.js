angular
    .module('BudgetCalculation')
    .controller("staffCtrl", ['$scope','$http', 'staffService', function($scope, $http, staffService) {
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
            }
            else if( window.submit_type == 2)  {
                vm.retrieveStaffSalaries();
            }
            else {
                vm.retrieveStaffSalaries();
            }
        }

        // Event Listeners
        $scope.$on('handleBudgetCalcSavedBroadcast', function() {
            vm.saveAllSalaries();
        });

        // Function implementations
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
                    saveItem(item);
                }else{
                    updateItem(item);
                }
            }
            console.log(vm.staffSalaryForms);
        }

        // Helper functions for saveAllSalaries
        function saveItem(item){
            staffService.saveItem(item);
        }

        function updateItem(item){
            staffService.updateItem(item);
        }
    }]);