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
        vm.editPerson = editPerson;
        vm.getQueryParams = getQueryParams;
        //vm.sortIcon = sortIcon;
        main();


        //////////////////////////////////////////////////////


        function main(){
            vm.getPersons();
        }

        // function sortIcon(){
        //     return vm.reverse ? "glyphicon-sort-by-alphabet-alt" : "glyphicon-sort-by-alphabet";
        // }

        function getPersons(){
            vm.loading = true;
            personService.listPersons()
                .success(function (data) {
                    vm.persons = data.results;
                    vm.nextPageUrl = data.next;
                    vm.loading = false;
                    console.log(vm.persons);
                });
        }

        function loadMorePersons(){
            vm.loading = true;
            personService.loadMore(vm.nextPageUrl, "&" + vm.getQueryParams().slice(1))
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

        function editPerson(person){
            vm.selectedPerson = person;
            var size = 'md';
            var modalInstance = $modal.open({
              animation: true,
              templateUrl: 'PersonEditModal.html',
              controller: 'ModalInstanceCtrl',
              size: size,
              resolve: {
                person: function () {
                    return person;
                }
              }
            });
            modalInstance.result.then(function (person) {
                    personService.savePerson(person)
                        .success(function (){
                            main();
                        });
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
