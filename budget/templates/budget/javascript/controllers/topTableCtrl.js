angular
    .module('BudgetCalculation')
    .controller("topTableCtrl", ['$scope','$http', function($scope, $http) {
        vm = this;

        vm.form = {};

        if( window.submit_type === 1) {
            var date = new Date();
            date.setDate(15);
            retrieveForm(date.getMonth(), date.getFullYear());
        }

        window.change = function () {
            var form_date = new Date(document.getElementById('month_year').value + '-15');
            retrieveForm(form_date.getMonth(), form_date.getFullYear());
        };

        $scope.$on('dateSetBroadcast', function(event, args){
            var form_date = args['date'];
            retrieveForm(form_date.getMonth(), form_date.getFullYear());
        });

        function retrieveForm(month, year) {

            return $http.get('/budget/api/budget_calculations/previous_data/' + window.border_station + '/' + (month+1) + '/' + year + '/') //month is zero indexed in javascript
                .success(function (data) {
                    vm.form = data;
                    $scope.$emit('lastBudgetTotalEmit', {total: data.last_months_total_cost });
                })
                .error(function (data, status, headers, config) {
                });
        }



    }]);