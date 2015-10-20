angular
    .module('AccountsMod')
    .controller('AccountsCtrl', ['$scope','$http', function($scope, $http) {
        var vm = this;

        vm.accounts = [{"email": "test1@example.com",
                        "first_name": "First1",
                        "last_name": "Last1",
                        "user_designation": "Super Administrator",
                        "date_created": "10.15.2015 15:37PM",
                        "last_login": "10.15.2015 15:37PM"},
                        {"email": "test2@example.com",
                         "first_name": "First2",
                         "last_name": "Last2",
                         "user_designation": "Super Administrator",
                         "date_created": "10.15.2015 15:37PM",
                         "last_login": "10.15.2015 15:37PM"}];
        vm.foo = "testing"


    }]);
