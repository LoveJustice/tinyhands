'use strict';

angular
    .module('DataEntry')
    .controller("irfListCtrl", ['$scope','$http','$timeout', 'irfService', "$modal", function($scope, $http, $timeout, irfService, $modal) {
        var vm = this;

        // Variable Declarations
        vm.loading = false;
        vm.reverse = false;
        vm.irfs = [];
        vm.searchValue = "";
        vm.nextPageUrl = "";
        vm.paginateBy = 25;
        vm.sortIcon = "/static/images/sortIcon.jpg";
        vm.selectedAddress = {};
        vm.sortColumn = "name";


        // Function Definitions
        vm.getIrfs = getIrfs;
        vm.searchIrfs = searchIrfs;
        vm.loadMoreIrfs = loadMoreIrfs;
        vm.getQueryParams = getQueryParams;
        vm.sortIcon = sortIcon;
        main();


        //////////////////////////////////////////////////////


        function main(){
            vm.getIrfs();
        }

        function sortIcon(){
            return vm.reverse ? "glyphicon-sort-by-alphabet-alt" : "glyphicon-sort-by-alphabet";
        }

        function getIrfs(){
            vm.loading = true;
            irfService.listIrfs(vm.getQueryParams())
                .success(function (data) {
                    vm.irfs = data.results;
                    vm.nextPageUrl = data.next;
                    vm.loading = false;
                });
        }

        function loadMoreIrfs(){
            vm.loading = true;
            irfService.listIrfs(vm.nextPageUrl, "&" + vm.getQueryParams().slice(1))
                .success(function (data) {
                    vm.irfs = vm.irfs.concat(data.results);
                    vm.nextPageUrl = data.next;
                    vm.loading = false;
                });
        }

        function searchIrfs(){
            vm.loading = true;
            irfService.listIrfs(vm.getQueryParams())
                .success(function (data) {
                    vm.irfs = data.results;
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