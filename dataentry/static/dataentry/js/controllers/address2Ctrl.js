'use strict';

angular
    .module('DataEntry')
    .controller("address2Ctrl", ['$scope','$http', 'address2Service', function($scope, $http, address2Service) {
        var vm = this;

        // Variable Declarations
        vm.addresses = [];
        vm.searchValue = "";
        vm.nextPageUrl = "";
        vm.paginateBy = 25;
        vm.sortIcon = "/static/images/sortIcon.jpg";

        // Function Definitions
        vm.getAddresses= getAddresses;
        vm.searchAddresses= searchAddresses;
        vm.loadMoreAddresses = loadMoreAddresses;
        main();
        console.log(vm.paginateBy);
        //////////////////////////////////////////////////////


        function main(){
            vm.getAddresses();
        }

        function getAddresses(){
            address2Service.listAddresses(vm.paginateBy)
                .success(function (data) {
                    vm.addresses = data.results;
                    vm.nextPageUrl = data.next;
                });
        }

        function loadMoreAddresses(){
            address2Service.loadMoreAddresses(vm.nextPageUrl, vm.paginateBy)
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
                });
        }

    }]);