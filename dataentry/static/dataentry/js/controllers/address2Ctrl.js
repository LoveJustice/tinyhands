'use strict';

angular
    .module('DataEntry')
    .controller("address2Ctrl", ['$scope','$http', 'address2Service', function($scope, $http, address2Service) {
        var vm = this;

        // Variable Declarations
        vm.addresses = [];
        vm.searchValue = "";

        // Function Definitions
        vm.getAddresses= getAddresses;
        vm.searchAddresses= searchAddresses;
        main();
        //////////////////////////////////////////////////////

        function main(){
            vm.getAddresses();
        }

        function getAddresses(){
            address2Service.listAddresses()
                .success(function (data) {
                    vm.addresses = data.slice(1,6);
                    console.log(vm.addresses);
                });
        }

        function searchAddresses(){
            console.log("clicked!");
            address2Service.searchAddresses(vm.searchValue)
                .success(function (data) {
                    vm.addresses = data;
                    console.log(data);
                });
        }

    }]);