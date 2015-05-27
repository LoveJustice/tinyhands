<<<<<<< HEAD
// service
=======
>>>>>>> demo/v0.3-local
angular
    .module('BudgetCalculation')
    .factory('staffService', staffService);

staffService.$inject = ['$http', '$q'];

function staffService($http, $q) {
	return {
<<<<<<< HEAD
=======
        retrieveOldStaffSalaries: retrieveOldStaffSalaries,
>>>>>>> demo/v0.3-local
		retrieveStaff: retrieveStaff,
        retrieveStaffSalaries: retrieveStaffSalaries,
        saveItem: saveItem,
        updateItem: updateItem
	};

	function retrieveStaff(borderStationId) {
        // grab all of the staff for this budgetCalcSheet
        return $http.get('/static_border_stations/api/border-stations/' + borderStationId + '/').
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

<<<<<<< HEAD
=======
    function retrieveOldStaffSalaries() {
        var staffPromise = $http({method: 'GET', url: '/static_border_stations/api/border-stations/' + window.border_station + '/'});
        var staffSalaryPromise = $http({method: 'GET', url: '/budget/api/budget_calculations/most_recent_form/' + window.budget_calc_id + '/'});
        return $q.all([staffPromise, staffSalaryPromise])
            .then(function (data) {
                return data;
            })
            .catch(function(data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

>>>>>>> demo/v0.3-local
    function retrieveStaffSalaries() {
        var staffPromise = $http({method: 'GET', url: '/static_border_stations/api/border-stations/' + window.border_station + '/'});
        var staffSalaryPromise = $http({method: 'GET', url: '/budget/api/budget_calculations/staff_salary/' + window.budget_calc_id + '/'});
        return $q.all([staffPromise, staffSalaryPromise])
            .then(function (data) {
                return data;
            })
            .catch(function(data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

    function saveItem(item) {
        item.budget_calc_sheet = window.budget_calc_id;
        return $http.post('/budget/api/budget_calculations/staff_salary/', item)
            .success(function (data, status) {
            })
            .error(function (data, status) {
                console.log("failure to create staff salary!");
                console.log(data, status);
            });
    }

    function updateItem(item) {
        return $http.put('/budget/api/budget_calculations/staff_salary/' + item.id + '/', item)
            .success(function(data, status) {

            })
            .error(function(data, status) {
<<<<<<< HEAD
                console.log("failure to update budget item!");
            });
    }
}
=======
                console.log(data, status);
                console.log("failure to update budget item!");
            });
    }
}
>>>>>>> demo/v0.3-local
