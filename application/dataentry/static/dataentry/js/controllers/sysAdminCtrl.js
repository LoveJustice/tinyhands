'use strict';

angular
    .module('DataEntry')
    .controller("sysAdminCtrl", ['$scope', function($scope) {
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
        //
        // vm.callTotals = function() {
        //     vm.address1_cutoff_value();
        //     vm.address1_limit_value();
        //     vm.address2_cutoff_value();
        //     vm.address2_limit_value();
        //     vm.person_cutoff_value();
        //     vm.person_limit_value();
        //     vm.phone_number_cutoff_value();
        //     vm.phone_number_limit_value();
        // }
        //
        // vm.address1_cutoff_value = function() {
        //     return vm.address1_cutoff;
        // };
        //
        // vm.address1_limit_value = function() {
        //     return vm.address1_limit;
        // };
        //
        // vm.address2_cutoff_value = function() {
        //     return vm.address2_cutoff;
        // };
        //
        // vm.address2_limit_value = function() {
        //     return vm.address2_limit;
        // };
        //
        // vm.person_cutoff_value = function() {
        //     return vm.person_cutoff;
        // };
        //
        // vm.person_limit_value = function() {
        //     return vm.person_limit;
        // };
        //
        // vm.phone_number_cutoff_value = function() {
        //     return vm.phone_number_cutoff;
        // };
        //
        // vm.phone_number_limit_value = function() {
        //     return vm.phone_number_limit;
        // };
        //
        // vm.retrieveForm = function(form) {
        //     sysAdminCtrlService.retrieveForm(form).then(function(promise){
        //         vm.form = promise.data;
        //         callTotals();
        //     });
        // };
        //
        // vm.updateForm = function() {
        //     sysAdminCtrlService.updateForm(form).then(function(promise){
        //         vm.form = promise.data;
        //     });
        // };

        vm.updateForm = function() {
            console.log(vm.form);
        };
    }]);
