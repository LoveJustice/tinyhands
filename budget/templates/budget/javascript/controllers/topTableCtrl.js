angular
    .module('BudgetCalculation')
    .controller("topTableCtrl", ['$scope','$http', function($scope, $http) {
        retrieveForm();

        vm = this;

        vm.form = {};

        function retrieveForm() {
            return $http.get('/budget/api/budget_calculations/previous_data/' + window.border_station + '/')
                .success(function (data) {
                    vm.form = data;
                })
                .error(function (data, status, headers, config) {
                });
        }



    }]);