angular
    .module('BudgetCalculation')
    .controller("staffCtrl", ['$scope','$http', '$location', '$window', '$q', function($scope, $http, $location, $window, $q) {
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
                vm.retrieveStaff(window.border_station);
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

        function retrieveStaff(borderStationId) {
            // grab all of the staff for this budgetCalcSheet
            $http.get('/static_border_stations/api/border-stations/' + borderStationId + '/').
                success(function (data) {
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
                }).
                error(function (data, status, headers, config) {
                    console.log(data, status, headers, config);
                });
        }

        function retrieveStaffSalaries() {
            var staffPromise = $http({method: 'GET', url: '/static_border_stations/api/border-stations/' + window.border_station + '/'});
            var staffSalaryPromise = $http({method: 'GET', url: '/budget/api/budget_calculations/staff_salary/' + window.budget_calc_id + '/'});
            $q.all([staffPromise, staffSalaryPromise]).then(function (data) {
                var staffData = data[0].data;
                var staffSalariesData = data[1].data;

                // Match staff to staffSalaries
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
            item.budget_calc_sheet = window.budget_calc_id;
            $http.post('/budget/api/budget_calculations/staff_salary/', item)
                .success(function(data, status) {
                })
                .error(function(data, status){
                    console.log("failure to create staff salary!");
                    console.log(data, status);
                });
        }

        function updateItem(item){
            $http.put('/budget/api/budget_calculations/staff_salary/' + item.id + '/', item)
                    .success(function(data, status) {
                    })
                    .error(function(data, status) {
                        console.log("failure to update budget item!");
                    });
        }



    }]);