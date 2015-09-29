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
        main();


        //////////////////////////////////////////////////////


        function main(){
            vm.getAddresses();
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
            console.log(params);
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
                console.log(address);
                address2Service.saveAddress(address)
                    .success(function (data){
                        main();
                    });
            });

        }


    }])

    .controller('ModalInstanceCtrl', function ($scope, $modalInstance, $http, address) {
        $scope.address = address;

        $scope.save = function () {
            $modalInstance.close($scope.address);
        };

        $scope.cancel = function () {
            $modalInstance.dismiss('cancel');
        };

        loadAddress1s();
        loadAddress2s();
        function loadAddress1s() {
            $http.get('/api/address1/all')
                .success(function (data) {
                    $scope.address1s = data;
                });
        }
        function loadAddress2s() {
            $http.get('/api/address2/')
                .success(function (data) {
                    $scope.address2s = data.results;
                    $scope.address2s.unshift({name: "Empty", id: -1})
                });
        }

    });