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
                    $scope.$emit('lastBudgetTotalEmit', {total: data.last_months_total_cost });
                })
                .error(function (data, status, headers, config) {
                });
        }



    }]);