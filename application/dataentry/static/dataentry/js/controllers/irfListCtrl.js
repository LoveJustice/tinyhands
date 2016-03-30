'use strict';

angular
    .module('DataEntry')
    .controller("irfListCtrl", ['$scope','$http','$timeout', '$location', 'irfService', function($scope, $http, $timeout, $location, irfService) {
        var vm = this;

        // Variable Declarations
        vm.header = "All IRFs";
        vm.loading = false;
        vm.reverse = false;
        vm.user = {};
        vm.irfs = [];
        vm.searchValue = "";
        vm.nextPageUrl = "";
        vm.paginateBy = 25;
        vm.sortIcon = "/static/images/sortIcon.jpg";
        vm.selectedAddress = {};
        vm.sortColumn = "irf_number";
        vm.timeZoneDifference ="+0545";
        vm.startDate = "";
        vm.endDate = "";
        vm.valid_date = false;


        // Function Definitions
        vm.getUser = getUser;
        vm.listIrfs = listIrfs;
        vm.loadMoreIrfs = loadMoreIrfs;
        vm.searchIrfs = searchIrfs;
        vm.deleteIrf = deleteIrf;
        vm.getQueryParams = getQueryParams;
        vm.sortIcon = sortIcon;
        vm.exportPhotos = exportPhotos;
        vm.validDate = validDate;
        main();


        //////////////////////////////////////////////////////


        function main(){
            if(window.search == 1){
                vm.searchValue = window.station_code;
                vm.header = "All IRFs for " + vm.searchValue;
            }
            vm.getUser();
            vm.listIrfs();
        }

        function getUser(){
            $http.get('/api/me/')
                .success(function(data){
                    vm.user = data
                });
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

        function listIrfs(){
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
            irfService.loadMoreIrfs(vm.nextPageUrl, "&" + vm.getQueryParams().slice(1))
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
                    if(vm.searchValue) {
                        vm.header = "All IRFs for " + vm.searchValue;
                    }
                    else {
                        vm.header = "All IRFs";
                    }
                    vm.nextPageUrl = data.next;
                    vm.loading = false;
                });
        }



        function deleteIrf(irf) {
            if(irf.confirmedDelete){
                vm.loading = true;
                irfService.deleteIrf(irf.delete_url)
                    .success(function(){
                        vm.listIrfs();
                        vm.loading = false;
                    })
                    .error(function(){
                        vm.loading = false;
                        alert("you did not have authorization to delete that IRF");
                    });
            }
            else{
                irf.confirmedDelete = true;
                setTimeout((function() {
                    console.log(irf);
                    irf.confirmedDelete = false;
                    $scope.$apply();
                }), 3000);
            }
        }

        function getQueryParams(){
            console.log("getting params...");
            var params = "";
            params += "?page_size=" + vm.paginateBy;
            if(vm.searchValue) {
                params += "&search=" + vm.searchValue;
            }

            if(vm.reverse){
                params += "&ordering=-" + vm.sortColumn;
            } else{
                params += "&ordering=" + vm.sortColumn;
            }
            return params;
        }

        function exportPhotos() {
            var listOfIrfNumbers = [];
            for (var irf of vm.irfs) {
                var date = new Date(irf.date_time_of_interception);
                var start = new Date(vm.startDate);
                var end = new Date(vm.endDate);
                if (date >= start && date <= end) {
                    listOfIrfNumbers.push((irf.irf_number));
                    //console.log(irf.irf_number);
                }
            }

            irfService.batchIrf(vm.startDate, vm.endDate)
            .success(function(data){
                console.log(String(data));
            })
            .error(function(){
                alert("Could not Export Photos");
            });
        }

        function validDate() {
            var start = new Date(vm.startDate);
            var end = new Date(vm.endDate);
            var oldest = new Date("01/01/2000");
            var latest = Date.now();
            if (vm.startDate == '' || vm.endDate == '' || start == "Invalid Date" || end == "Invalid Date" || end < start || start < oldest || start > latest || end < oldest || end > latest) {
                vm.valid_date = false;
            } else {
                vm.valid_date = true;
            }
        }
    }]);
