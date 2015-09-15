angular
    .module('BudgetCalculation')
    .controller("topTableCtrl", ['$scope','$http', function($scope, $http) {
        var vm = this;

        // Variable Definitions
        vm.form = {};

        // Function Definitions
        vm.main = main;
        vm.retrieveForm = retrieveForm;

        // Calling the main function
        vm.main();

        function main(){
            if( window.submit_type === 1) { // If this is a new form, then they are creating it for this month
                var date = new Date();
                date.setDate(15); // Set the date of the month to the 15th
                retrieveForm(date.getMonth(), date.getFullYear());
            }
        }

        // Event Listeners
        $scope.$on('dateSetBroadcast', function(event, args){ // When the mainCtrl receives a date from a saved form, it sends the value over a broadcast
            var form_date = args['date'];
            console.log(form_date);
            retrieveForm(form_date.getMonth(), form_date.getFullYear());
        });

        //Global Function Definition
        window.change = function () { // This watches the month_year element on the page... its hack-y, but ng-change doesn't support date types for some reason
            var form_date = new Date(document.getElementById('month_year').value + '-15');
            retrieveForm(form_date.getMonth(), form_date.getFullYear());
        };

        // I didn't bother making a service for this since there is only one http call
        function retrieveForm(month, year) {
            return $http.get('/budget/api/budget_calculations/previous_data/' + window.border_station + '/' + (month+1) + '/' + year + '/') //month is zero indexed in javascript
                .success(function (data) {
                    vm.form = data;
                    console.log(data);
                    $scope.$emit('lastBudgetTotalEmit', {total: data.last_months_total_cost });
                })
                .error(function (data, status, headers, config) {
                });
        }
    }]);
