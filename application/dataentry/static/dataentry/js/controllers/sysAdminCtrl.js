'use strict';

angular
    .module('DataEntry')
    .controller("sysAdminCtrl", ['$scope', '$http', '$window', 'sysAdminService', function($scope, $http, $window, sysAdminService) {
        var vm = this;

        vm.form = {};

        // vm.address1_cutoff = 70;
        // vm.address1_limit = 5;
        // vm.address2_cutoff = 70;
        // vm.address2_limit = 5;
        // vm.person_cutoff = 90;
        // vm.person_limit = 10;
        // vm.phone_number_cutoff = 0;
        // vm.phone_number_limit = 0;

        function callTotals() {
            vm.address1_cutoff_value();
            vm.address1_limit_value();
            vm.address2_cutoff_value();
            vm.address2_limit_value();
            vm.person_cutoff_value();
            vm.person_limit_value();
            vm.phone_number_cutoff_value();
            vm.phone_number_limit_value();
        }

        // function getForm() {
        //     return {"address1_cutoff": vm.address1_cutoff_value(),
        //             "address1_limit": vm.address1_limit_value(),
        //             "address2_cutoff": vm.address2_cutoff_value(),
        //             "address2_limit": vm.address2_limit_value(),
        //             "person_cutoff": vm.person_cutoff_value(),
        //             "person_limit": vm.person_limit_value(),
        //             "phone_number_cutoff": vm.phone_number_cutoff_value(),
        //             "phone_number_limit": vm.phone_number_limit_value()}
        // }

        function getForm() {
            return {"address1_cutoff": angular.element('#address1_cutoff').val(),
                    "address1_limit": angular.element('#address1_limit').val(),
                    "address2_cutoff": angular.element('#address2_cutoff').val(),
                    "address2_limit": angular.element('#address2_limit').val(),
                    "person_cutoff": angular.element('#person_cutoff').val(),
                    "person_limit": angular.element('#person_limit').val(),
                    "phone_number_cutoff": angular.element('#phone_number_cutoff').val(),
                    "phone_number_limit": angular.element('#phone_number_limit').val()}
        }

        vm.address1_cutoff_value = function() {
            return vm.address1_cutoff;
        };

        vm.address1_limit_value = function() {
            return vm.address1_limit;
        };

        vm.address2_cutoff_value = function() {
            return vm.address2_cutoff;
        };

        vm.address2_limit_value = function() {
            return vm.address2_limit;
        };

        vm.person_cutoff_value = function() {
            return vm.person_cutoff;
        };

        vm.person_limit_value = function() {
            return vm.person_limit;
        };

        vm.phone_number_cutoff_value = function() {
            return vm.phone_number_cutoff;
        };

        vm.phone_number_limit_value = function() {
            return vm.phone_number_limit;
        };

        vm.retrieveForm = function() {
            sysAdminService.retrieveForm().then(function(promise){
                vm.form = promise.data;
                //console.log("RetrieveForm:", vm.form);
                //callTotals();
            });
        };

        vm.updateForm = function() {
            vm.form = getForm();
            sysAdminService.updateForm(vm.form).then(function(promise){
                vm.form = promise.data;
                //console.log("UpdateForm:", vm.form);
                $window.location.assign('/data-entry/sysadminsettings/1/');
            });
        };

        vm.retrieveForm();
        //callTotals();

    }]);
