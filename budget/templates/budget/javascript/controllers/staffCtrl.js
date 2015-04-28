angular
    .module('BudgetCalculation')
    .controller("staffCtrl", ['$scope','$http', '$location', '$window', '$q', 'staffService', function($scope, $http, $location, $window, $q, staffService) {
        // get staff for a border_station http://localhost:8000/static_border_stations/api/border-stations/0/
        var vm = this;
        vm.staffSalaryForms = [];
        vm.staffTotal = 0;

        vm.totalSalaries = totalSalaries;
        vm.saveAllSalaries = saveAllSalaries;
        vm.retrieveStaff = retrieveStaff;

        main();

        $scope.$on('handleBudgetCalcSavedBroadcast', function(event, args) {
            vm.saveAllSalaries();
        });

        function main(){
            if( window.submit_type == 1 ) {
                vm.retrieveStaff();
            }
            else if( window.submit_type == 2)  {
                retrieveStaffSalaries();
            }
            else {
                retrieveStaffSalaries();
            }
        }

        function totalSalaries(){
            var acc = 0;
            for(var x = 0; x < vm.staffSalaryForms.length; x++){
                acc += vm.staffSalaryForms[x].salary;
            }
            vm.staffTotal = acc;

            $scope.$emit('handleSalariesTotalChangeEmit', {total: acc});
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
                    console.log(promise);
                    var staffData = promise[0].data;
                    var staffSalariesData = promise[1].data;

                    for(var person = 0; person < staffSalariesData.length; person++) {
                        for (var x = 0; x < staffData.length; x++) {
                            if (staffData[x].id === staffSalariesData[person].staff_person) {
                                staffSalariesData[person].name = staffData[x].first_name + ' ' + staffData[x].last_name;
                                console.log(staffSalariesData[person].name);
                            }
                        }
                        vm.staffSalaryForms.push(staffSalariesData[person])
                    }
                });
        }


        function saveAllSalaries(){
            for(var person = 0; person < vm.staffSalaryForms.length; person++){
                item = vm.staffSalaryForms[person];
                if(!item.id){
                    saveItem(item);
                }else{
                    updateItem(item);
                }
            }
        }

        function saveItem(item){
            staffService.saveItem(item);
        }

        function updateItem(item){
            staffService.updateItem(item);
        }
    }]);