// service
angular
    .module('BudgetCalculation')
    .factory('mainCtrlService', mainCtrlService);

mainCtrlService.$inject = ['$http'];

function mainCtrlService($http) {
    return {
        retrieveForm: retrieveForm,
        deletePost: deletePost,
        updateForm: updateForm,
        createForm: createForm
	};


    function retrieveForm(id) {
        return $http.get('/budget/api/budget_calculations/' + id + '/').
            success(function (data) {
                return data;
            }).
            error(function (data, status, headers, config) {
            });
    }

    function deletePost(id) {
        return $http.delete('/budget/api/budget_calculations/' + id + '/').
            success(function (data, status, headers, config) {
            }).
            error(function (data, status, headers, config) {
            })
    }

    function updateForm(id, form) {
        return $http.put('/budget/api/budget_calculations/' + id + '/', form)
            .success(function(data, status) {
                return data;
            })
            .error(function(data, status) {
                //console.log("fail");
            });
    }

    function createForm(form) {
        return $http.post('/budget/api/budget_calculations/', form)
            .success(function(data, status) {
                return data;
            })
            .error(function(data, status) {
                //console.log("fail create");
            });
    }

}
