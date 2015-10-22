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
        vm.permissions = [{"full_name": "test1",
                          "user_designation": "Super Administrator",
                          "irf_view": true,
                          "irf_add": true,
                          "irf_edit": true,
                          "irf_delete": true,
                          "vif_view": true,
                          "vif_add": true,
                          "vif_edit": true,
                          "vif_delete": true,
                          "order_stations_view": true,
                          "order_stations_add": true,
                          "order_stations_edit": true,
                          "order_stations_delete": true,
                          "accounts_manage": true,
                          "receive_mail": true,
                          "vdc_message": true,
                          "budget_manage": true}];
        vm.foo = "testing";


    }]);
