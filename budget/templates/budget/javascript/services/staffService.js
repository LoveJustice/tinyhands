// service
angular
    .module('BudgetCalculation')
    .factory('staffService', staffService);

staffService.$inject = ['$http'];

function staffService($http) {
	return {
		retrieveStaff: retrieveStaff
	};

	// TODO: This has not been refactored properly yet!
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
}
