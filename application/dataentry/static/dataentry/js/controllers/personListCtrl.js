angular
    .module('DataEntry')
    .controller("personListCtrl", ['$scope','$http','$timeout', '$location', '$window', 'personService', function($scope, $http, $timeout, $location, $window, personService) {
        var vm = this;


        // Variable Declarations
        vm.loading = false;
        vm.reverse = false;
        vm.persons = [];
        vm.searchValue = "";
        vm.nextPageUrl = "";
        vm.paginateBy = 25;
        vm.sortIcon = "/static/images/sortIcon.jpg";
        vm.selectedPerson = {};
        vm.sortColumn = "name";


        // Function Definitions
        vm.getPersons = getPersons;
        vm.searchPersons = searchPersons;
        vm.loadMorePersons = loadMorePersons;
        vm.getForm = getForm;
        vm.getQueryParams = getQueryParams;
        vm.sortIcon = sortIcon;
        main();


        //////////////////////////////////////////////////////


        function main(){
            vm.getPersons();
        }

        function sortIcon(){
            return vm.reverse ? "glyphicon-sort-by-alphabet-alt" : "glyphicon-sort-by-alphabet";
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
            console.log(params)
            return params;
        }


        function getPersons(){
            vm.loading = true;
            personService.listPersons(vm.getQueryParams())
                .success(function (data) {
                    vm.persons = data.results;
                    vm.nextPageUrl = data.next;
                    vm.loading = false;
                    //console.log(vm.persons);
                });
        }

        function getForm(person){
            vm.loading = true;
            console.log(personService.getForm(person));
        }

        function loadMorePersons(){
            vm.loading = true;
            personService.loadMorePersons(vm.nextPageUrl, "&" + vm.getQueryParams().slice(1))
                .success(function (data) {
                    vm.persons = vm.persons.concat(data.results);
                    vm.nextPageUrl = data.next;
                    vm.loading = false;
                });
        }

        function searchPersons(){
            vm.loading = true;
            personService.searchPersons(vm.getQueryParams())
                .success(function (data) {
                    vm.persons = data.results;
                    vm.nextPageUrl = data.next;
                    vm.loading = false;
                });
        }
    }])

    .controller('ModalInstanceCtrl', function ($scope, $modalInstance, $http, person) {
        $scope.person = angular.copy(person);

        $scope.save = function () {
            $modalInstance.close($scope.person);
        };

        $scope.cancel = function () {
            $modalInstance.dismiss('close');
        };
    });
