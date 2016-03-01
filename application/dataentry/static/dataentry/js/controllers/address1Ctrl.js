'use strict';

angular
    .module('DataEntry')
    .controller("address1Ctrl", ['$scope','$http','$timeout', 'address1Service', "$modal", function($scope, $http, $timeout, address1Service, $modal) {
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
        vm.sortColumn = "";


        // Function Definitions
        vm.getAddresses = getAddresses;
        vm.searchAddresses = searchAddresses;
        vm.loadMoreAddresses = loadMoreAddresses;
        vm.editAddress1 = editAddress1;
        vm.getQueryParams = getQueryParams;
        vm.sortIcon = sortIcon;
        main();


        //////////////////////////////////////////////////////


        function main(){
            vm.getAddresses();
        }

        function sortIcon(column){
            if(column === vm.sortColumn){
                switch (column) {
                    case "latitude":
                    case "longitude":
                        return vm.reverse ? "glyphicon-sort-by-order-alt" : "glyphicon-sort-by-order";
                    case "name":
                    case "level":
                    case "completed":
                        return vm.reverse ? "glyphicon-sort-by-alphabet-alt" : "glyphicon-sort-by-alphabet";
                    default:
                        return "glyphicon-sort";
                }
            }
            return "glyphicon-sort";
        }

        function getAddresses(){
            vm.loading = true;
            address1Service.listAddresses(vm.getQueryParams())
                .success(function (data) {
                    vm.addresses = data.results;
                    vm.nextPageUrl = data.next;
                    vm.loading = false;
                });
        }

        function loadMoreAddresses(){
            vm.loading = true;
            address1Service.loadMoreAddresses(vm.nextPageUrl, "&" + vm.getQueryParams().slice(1))
                .success(function (data) {
                    vm.addresses = vm.addresses.concat(data.results);
                    vm.nextPageUrl = data.next;
                    vm.loading = false;
                });
        }

        function searchAddresses(){
            vm.loading = true;
            address1Service.searchAddresses(vm.getQueryParams())
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

        function editAddress1(address){
            vm.selectedAddress = address;
            var size = 'md';
            var modalInstance = $modal.open({
              animation: true,
              templateUrl: 'address1EditModal.html',
              controller: 'ModalInstanceCtrl',
              size: size,
              resolve: {
                address: function () {
                    return address;
                }
              }
            });
            modalInstance.result.then(function (address) {
                    address1Service.saveAddress(address)
                        .success(function (){
                            main();
                        })
                        .error(function (){
                            alert(address.name);

                        });
            });

        }
    }])

    .controller('ModalInstanceCtrl', function ($scope, $modalInstance, $http, address) {
        $scope.address = angular.copy(address);

        $scope.save = function () {
            $modalInstance.close($scope.address);
        };

        $scope.cancel = function () {
            $modalInstance.dismiss('close');
        };
    });