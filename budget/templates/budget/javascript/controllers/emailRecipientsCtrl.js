angular
    .module('BudgetCalculation')
    .controller("emailRecipientsCtrl", ['$scope','$http', function($scope, $http) {
        vm = this;

        retrieveForm();

        vm.staff = {};
        vm.committeeMembers = {};

        function retrieveForm() {
            return $http.get('/budget/api/budget_calculations/money_distribution/' + window.border_station + '/')
                .success(function (data) {
                    console.log(data);
                    vm.committeeMembers = data.committee_members;
                    vm.staff = data.staff_members;
                })
                .error(function (data, status, headers, config) {
                });
        }



    }]);