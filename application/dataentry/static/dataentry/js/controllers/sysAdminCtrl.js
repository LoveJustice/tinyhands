'use strict';

angular
    .module('DataEntry')
    .controller("sysAdminCtrl", ['$scope', '$http', '$window', 'sysAdminService', function($scope, $http, $window, sysAdminService) {
        var vm = this;

        vm.form = {};

        function getForm() {
            return {"address1_cutoff": angular.element('#address1_cutoff').val(),
                    "address1_limit": angular.element('#address1_limit').val(),
                    "address2_cutoff": angular.element('#address2_cutoff').val(),
                    "address2_limit": angular.element('#address2_limit').val(),
                    "person_cutoff": angular.element('#person_cutoff').val(),
                    "person_limit": angular.element('#person_limit').val()}
                    // "phone_number_cutoff": angular.element('#phone_number_cutoff').val(),
                    // "phone_number_limit": angular.element('#phone_number_limit').val()}
        }

        vm.retrieveForm = function() {
            sysAdminService.retrieveForm().then(function(promise){
                vm.form = promise.data;
            });
        };

        vm.updateForm = function() {
            vm.form = getForm();
            sysAdminService.updateForm(vm.form).then(function(promise){
                vm.form = promise.data;
                $window.location.assign('/data-entry/sysadminsettings/1/');
            });
        };

        vm.retrieveForm();

    }]);
