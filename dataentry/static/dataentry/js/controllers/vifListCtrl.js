'use strict';

angular
    .module('DataEntry')
    .controller("vifListCtrl", ['$scope','$http','$timeout', 'vifService', function($scope, $http, $timeout, vifService) {
        var vm = this;

        // Variable Declarations
        vm.loading = false;
        vm.reverse = false;
        vm.vifs = [];
        vm.user = {};
        vm.searchValue = "";
        vm.nextPageUrl = "";
        vm.paginateBy = 25;
        vm.sortIcon = "/static/images/sortIcon.jpg";
        vm.selectedAddress = {};
        vm.sortColumn = "vif_number";


        // Function Definitions
        vm.getUser = getUser;
        vm.listVifs = listVifs;
        vm.loadMoreVifs = loadMoreVifs;
        vm.searchVifs = searchVifs;
        vm.deleteVif = deleteVif;
        vm.getQueryParams = getQueryParams;
        vm.sortIcon = sortIcon;
        main();


        //////////////////////////////////////////////////////


        function main(){
            vm.listVifs();
            vm.getUser();
        }

        function getUser(){
            vm.user = {
                "email": "asdasd",
                "permission_irf_view": true,
                "permission_irf_add": true,
                "permission_irf_edit": true,
                "permission_irf_delete": true,
                "permission_vif_view": true,
                "permission_vif_add": true,
                "permission_vif_edit": true,
                "permission_vif_delete": true
            };
        }

        function sortIcon(column, name){
            if(name === vm.sortColumn){
                switch (column) {
                    case "number":
                        return vm.reverse ? "glyphicon-sort-by-order-alt" : "glyphicon-sort-by-order";
                    case "letter":
                        return vm.reverse ? "glyphicon-sort-by-alphabet-alt" : "glyphicon-sort-by-alphabet";
                    default:
                        return "glyphicon-sort";
                }
            }
            return "glyphicon-sort";
        }

        function listVifs(){
            vm.loading = true;
            vifService.listVifs(vm.getQueryParams())
                .success(function (data) {
                    vm.vifs = data.results;
                    vm.nextPageUrl = data.next;
                    vm.loading = false;
                });
        }

        function loadMoreVifs(){
            vm.loading = true;
            vifService.loadMoreVifs(vm.nextPageUrl, "&" + vm.getQueryParams().slice(1))
                .success(function (data) {
                    vm.vifs = vm.vifs.concat(data.results);
                    vm.nextPageUrl = data.next;
                    vm.loading = false;
                });
        }

        function searchVifs(){
            vm.loading = true;
            vifService.listVifs(vm.getQueryParams())
                .success(function (data) {
                    vm.vifs = data.results;
                    vm.nextPageUrl = data.next;
                    vm.loading = false;
                });
        }

        function deleteVif(vif) {
            if(vif.confirmedDelete){
                vm.loading = true;
                vifService.deleteVif(vif.delete_url)
                    .success(function(){
                        vm.listVifs();
                        vm.loading = false;
                    })
                    .error(function(){
                        vm.loading = false;
                        alert("you did not have authorization to delete that VIF");
                    });
            }
            else{
                vif.confirmedDelete = true;
            }
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