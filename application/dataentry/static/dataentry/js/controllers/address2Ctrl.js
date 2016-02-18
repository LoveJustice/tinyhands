'use strict';

angular
    .module('DataEntry')
    .controller("address2Ctrl", ['$scope','$http','$timeout', 'address2Service', "$modal", function($scope, $http, $timeout, address2Service, $modal) {
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
        vm.editAddress2 = editAddress2;
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
                    case "canonical_name.name":
                    case "district.name":
                    case "verified":
                        return vm.reverse ? "glyphicon-sort-by-alphabet-alt" : "glyphicon-sort-by-alphabet";
                    default:
                        return "glyphicon-sort";
                }
            }
            return "glyphicon-sort";
        }

        function getAddresses(){
            vm.loading = true;
            address2Service.listAddresses(vm.getQueryParams())
                .success(function (data) {
                    vm.addresses = data.results;
                    vm.nextPageUrl = data.next;
                    vm.loading = false;
                });
        }

        function loadMoreAddresses(){
            vm.loading = true;
            address2Service.loadMoreAddresses(vm.nextPageUrl, "&" + vm.getQueryParams().slice(1))
                .success(function (data) {
                    vm.addresses = vm.addresses.concat(data.results);
                    vm.nextPageUrl = data.next;
                    vm.loading = false;
                });
        }

        function searchAddresses(){
            vm.loading = true;
            address2Service.searchAddresses(vm.getQueryParams())
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
            if(vm.sortColumn){
                if(vm.reverse){
                    params += "&ordering=-" + (vm.sortColumn.replace(".","__"));
                } else{
                    params += "&ordering=" + (vm.sortColumn.replace(".","__"));
                }
            }
            return params;
        }

        function editAddress2(address){
            vm.selectedAddress = address;
            var size = 'md';
            var modalInstance = $modal.open({
              animation: true,
              templateUrl: 'address2EditModal.html',
              controller: 'ModalInstanceCtrl',
              size: size,
              resolve: {
                address: function () {
                    return address;
                }
              }
            });
            modalInstance.result.then(function (address) {
                    address2Service.saveAddress(address)
                        .success(function (){
                            main();
                        })
                        .error(function (){
                            alert(address);

                        });
            });

        }


    }])

    .controller('ModalInstanceCtrl', function ($scope, $modalInstance, $http, address) {
        $scope.address = angular.copy(address);


        $scope.save = function () {
            // this is so we can save null cannon names
            if($scope.address.canonical_name === "" || $scope.address.canonical_name == undefined){
                $scope.address.canonical_name = {id: -1, name: "Empty"};
            }
            $modalInstance.close($scope.address);
        };

        $scope.cancel = function () {
            $modalInstance.dismiss('close');
        };

        $scope.getFuzzyAddress1s = function(val) {
            return $http.get('/api/address1/fuzzy/?district=' + val)
                .then(function(response){
                    return response.data;
                });
        };

        $scope.getFuzzyAddress2s = function(val) {
            return $http.get('/api/address2/fuzzy/?vdc=' + val)
                .then(function(response){
                    return response.data;
                });
        };
    });