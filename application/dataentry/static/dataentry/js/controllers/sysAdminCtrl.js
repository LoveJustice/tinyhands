'use strict';

angular
    .module('DataEntry')
    .controller("sysAdminCtrl", ['$scope', function($scope) {
        var vm = this;

        vm.form = {};

        vm.updateForm = function() {
            console.log(vm.form);
        };
    }]);
