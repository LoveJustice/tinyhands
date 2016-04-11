'use strict';

angular
    .module('DataEntry')
    .controller("irfListCtrl", ['$scope','$http','$timeout', '$location', '$window', 'irfService', function($scope, $http, $timeout, $location, $window, irfService) {
        var vm = this;

        // Variable Declarations
        vm.endDate = "";
        vm.endDay = "";
        vm.endMonth = "";
        vm.endYear = "";
        vm.header = "All IRFs";
        vm.irfs = [];
        vm.loading = false;
        vm.nextPageUrl = "";
        vm.paginateBy = 25;
        vm.searchValue = "";
        vm.selectedAddress = {};
        vm.sortColumn = "irf_number";
        vm.sortIcon = "/static/images/sortIcon.jpg";
        vm.startDate = "";
        vm.startDay = "";
        vm.startMonth = "";
        vm.startYear = "";
        vm.timeZoneDifference ="+0545";
        vm.reverse = false;
        vm.user = {};
        vm.valid_date = false;

        // Function Definitions
        vm.deleteIrf = deleteIrf;
        vm.exportPhotos = exportPhotos;
        vm.getDays = getDays;
        vm.getMonths = getMonths;
        vm.getQueryParams = getQueryParams;
        vm.getUser = getUser;
        vm.getYears = getYears;
        vm.listIrfs = listIrfs;
        vm.loadMoreIrfs = loadMoreIrfs;
        vm.searchIrfs = searchIrfs;
        vm.sortIcon = sortIcon;
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

        function exportPhotos() {
            var monthArray = ['January','February','March','April','May','June','July','August','September','October',
            'November','December'];

            var startMonth = vm.startMonth;
            startMonth = monthArray.indexOf(startMonth) + 1;
            if (startMonth.toString().length == 1) {
                startMonth = '0' + startMonth;
            }

            var startDay = vm.startDay.toString();
            if (vm.startDay.length == 1) {
                startDay = '0' + startDay;
            }

            var endMonth = vm.endMonth;
            endMonth = monthArray.indexOf(endMonth) + 1;
            if (endMonth.toString().length == 1) {
                endMonth = '0' + endMonth;
            }

            var endDay = vm.endDay.toString();
            if (vm.endDay.length == 1) {
                endDay = '0' + endDay;
            }

            vm.startDate = startMonth + '-' + startDay + '-' + vm.startYear;
            vm.endDate = endMonth + '-' + endDay + '-' + vm.endYear;

            var url = '/api/batch/' + vm.startDate + '/' + vm.endDate;
            $window.location.href = url;
        }

        function getDays(month, year) {
            var days = ['',1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30];
            if (month == '') {
                return '';
            } else if (month == 'January' || month == 'March' || month=='May' || month == 'July' || month == 'August' || month == 'October' || month == 'December') {
                days.push(31);
            } else if (month == 'February') {
                days.pop();
                if (year != '' && year % 4 != 0) {
                    days.pop();
                }
            }
            return days;
        }

        function getMonths() {
            return ['','January','February','March','April','May','June','July','August','September','October','November','December'];
        }

        function getQueryParams(){
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

        function getUser(){
            $http.get('/api/me/')
                .success(function(data){
                    vm.user = data
                });
        }

        function getYears() {
            return ['', 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016];
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

        function validDate() {
            var monthArray = ['January','February','March','April','May','June','July','August','September','October',
            'November','December'];

            if (vm.startMonth == '' || vm.startDay == '' || vm.startYear == '' || vm.endMonth == '' || vm.endDay == '' || vm.endYear == '') {
                return false;
            } else if (vm.startYear > vm.endYear) {
                return false;
            } else if (vm.startYear == vm.endYear && monthArray.indexOf(vm.startMonth) > monthArray.indexOf(vm.endMonth)) {
                return false;
            } else if (vm.startYear == vm.endYear && vm.startMonth == vm.endMonth && vm.startDay > vm.endDay) {
                return false;
            } else {
                return true;
            }
        }

    }]);
