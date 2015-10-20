'use strict';

angular
    .module('DataEntry')
    .controller("irfListCtrl", ['$scope','$http','$timeout', 'irfService', "$modal", function($scope, $http, $timeout, irfService, $modal) {
        var vm = this;

        // Variable Declarations
        vm.loading = false;
        vm.reverse = false;
        vm.addresses = [];
        vm.searchValue = "";
        vm.nextPageUrl = "";
        vm.paginateBy = 25;
        vm.sortIcon = "/static/images/sortIcon.jpg";
        vm.selectedAddress = {};
        vm.sortColumn = "name";


        // Function Definitions
        vm.getAddresses = getAddresses;
        vm.searchAddresses = searchAddresses;
        vm.loadMoreAddresses = loadMoreAddresses;
        vm.getQueryParams = getQueryParams;
        vm.sortIcon = sortIcon;
        main();


        //////////////////////////////////////////////////////


        function main(){
            vm.getAddresses();
        }

        function sortIcon(){
            return vm.reverse ? "glyphicon-sort-by-alphabet-alt" : "glyphicon-sort-by-alphabet";
        }

        function getAddresses(){
            vm.loading = true;
            irfService.listAddresses(vm.getQueryParams())
                .success(function (data) {
                    vm.addresses = data.results;
                    vm.nextPageUrl = data.next;
                    vm.loading = false;
                });
        }

        function loadMoreAddresses(){
            vm.loading = true;
            irfService.loadMoreAddresses(vm.nextPageUrl, "&" + vm.getQueryParams().slice(1))
                .success(function (data) {
                    vm.addresses = vm.addresses.concat(data.results);
                    vm.nextPageUrl = data.next;
                    vm.loading = false;
                });
        }

        function searchAddresses(){
            vm.loading = true;
            irfService.searchAddresses(vm.getQueryParams())
                .success(function (data) {
                    vm.addresses = data.results;
                    vm.nextPageUrl = data.next;
                    vm.loading = false;
                });
        }

        function getQueryParams(){
            var params = "";
            params += "?page_size=" + vm.paginateBy;
            if(vm.searchValue){
                params += "&search=" + vm.searchValue;
            }
            if(vm.reverse){
                params += "&ordering=-" + vm.sortColumn;
            } else{
                params += "&ordering=" + vm.sortColumn;
            }
            return params;
        }
    }]);