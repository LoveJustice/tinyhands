angular
    .module('BudgetCalculation')
    .factory('otherItemsService', staffService);

staffService.$inject = ['$http'];

function staffService($http) {
	return {
        removeItem: removeItem,
        retrieveNewForm: retrieveNewForm,
        retrieveForm: retrieveForm,
        saveItem: saveItem,
        updateItem: updateItem

	};

    function removeItem(itemId) {
        return $http.delete('/budget/api/budget_calculations/items_detail/' + itemId + '/').
                success(function (data) {
                    return data;
                }).
                error(function (data, status, headers, config) {
                    console.log(data, status, headers, config);
                });
    }

    function retrieveNewForm() {
        return $http.get('/budget/api/budget_calculations/most_recent_form/' + window.budget_calc_id + '/').
            success(function (data) {
                return data;
            }).
            error(function (data, status) {
                console.log(data, status);
            });
    }

    function retrieveForm(id) {
        // grab all of the otherBudgetItems for this budgetCalcSheet
        return $http.get('/budget/api/budget_calculations/items_detail/' + id + '/')
            .success(function (data) {
                return data;
            })
            .error(function (data, status, headers, config) {
                console.log(data, status, headers, config);
            });
    }

    function saveItem(item){
        item.budget_item_parent = window.budget_calc_id;
        return $http.post('/budget/api/budget_calculations/items_list/', item)
            .success(function(data) {
                return item.id = data.id;
            })
            .error(function(data, status){
                console.log(data, status);
                console.log("failure to create budget item!");
            });
    }

    function updateItem(item){
        return $http.put('/budget/api/budget_calculations/items_detail/' + item.id + '/', item)
            .success(function(data, status) {
                console.log(data, status);
            })
            .error(function(data, status) {
                console.log(data, status);
            });
    }
}