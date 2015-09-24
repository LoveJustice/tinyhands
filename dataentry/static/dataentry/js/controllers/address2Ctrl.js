'use strict';

angular
    .module('DataEntry')
    .controller("address2Ctrl", ['$scope','$http','$timeout', 'address2Service', "$modal", function($scope, $http, $timeout, address2Service, $modal) {
        var vm = this;

        // Variable Declarations
        vm.loading = false;
        vm.addresses = [];
        vm.searchValue = "";
        vm.nextPageUrl = "";
        vm.paginateBy = 25;
        vm.sortIcon = "/static/images/sortIcon.jpg";
        vm.selectedAddress = {};

        // Function Definitions
        vm.getAddresses = getAddresses;
        vm.searchAddresses = searchAddresses;
        vm.loadMoreAddresses = loadMoreAddresses;
        vm.editAddress2 = editAddress2;
        main();


        //////////////////////////////////////////////////////


        function main(){
            vm.getAddresses();
        }

        function getAddresses(){
            vm.loading = true;
            address2Service.listAddresses(vm.paginateBy)
                .success(function (data) {
                    vm.addresses = data.results;
                    vm.nextPageUrl = data.next;
                    vm.loading = false;
                });
        }

        function loadMoreAddresses(){
            vm.loading = true;
            address2Service.loadMoreAddresses(vm.nextPageUrl, vm.paginateBy)
                .success(function (data) {
                    vm.addresses = vm.addresses.concat(data.results);
                    vm.nextPageUrl = data.next;
                    vm.loading = false;
                });
        }

        function searchAddresses(){
            vm.loading = true;
            address2Service.searchAddresses(vm.paginateBy, vm.searchValue)
                .success(function (data) {
                    vm.addresses = data.results;
                    vm.nextPageUrl = data.next;
                    vm.loading = false;
                });
        }

        function editAddress2(address){
            vm.selectedAddress = address;
            var size = 'sm';
            var modalInstance = $modal.open({
              animation: true,
              templateUrl: 'myModalContent.html',
              controller: 'ModalInstanceCtrl',
              size: size,
              resolve: {
                address: function () {
                    return "hello";
                }
              }
            });
        }


    }]);

angular
    .module('DataEntry')
        .controller('ModalInstanceCtrl', function ($scope, $modalInstance, address) {

        console.log(address);
      $scope.address = address;
});