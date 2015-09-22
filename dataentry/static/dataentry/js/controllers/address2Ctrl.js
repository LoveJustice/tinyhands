'use strict';

angular
    .module('DataEntry')
    .controller("address2Ctrl", ['$scope','$http', 'address2Service', function($scope, $http, address2Service) {
        var vm = this;

        // Variable Declarations
        vm.addresses = [];
        vm.searchValue = "";
        vm.nextPageUrl = "";

        // Function Definitions
        vm.getAddresses= getAddresses;
        vm.searchAddresses= searchAddresses;
        vm.loadMoreAddresses = loadMoreAddresses;
        main();
        //////////////////////////////////////////////////////

        function main(){
            vm.getAddresses();
        }

        function getAddresses(){
            address2Service.listAddresses()
                .success(function (data) {
                    vm.addresses = data.results;
                    vm.nextPageUrl = data.next;
                    console.log(data.results);
                });
        }

        function loadMoreAddresses(){
            address2Service.loadMoreAddresses(vm.nextPageUrl)
                .success(function (data) {
                    vm.addresses = vm.addresses.concat(data.results);
                    vm.nextPageUrl = data.next;
                });
        }

        function searchAddresses(){
            address2Service.searchAddresses(vm.searchValue)
                .success(function (data) {
                    vm.addresses = data.results;
                    vm.nextPageUrl = data.next;
                    console.log(data);
                });
        }

    }]);