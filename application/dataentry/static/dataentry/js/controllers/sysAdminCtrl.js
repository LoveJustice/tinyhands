'use strict';

angular
    .module('DataEntry')
    .controller("sysAdminCtrl", ['$scope','$http','$timeout', function($scope, $http, $timeout) {

        // Variable Declarations
        // var form = {
        //     address1_cutoff = 0,
        //     address1_limit = 0,
        //     address2_cutoff = 0,
        //     address2_limit = 0,
        //     person_cutoff = 0,
        //     person_limit = 0,
        //     phone_number_cutoff = 0,
        //     phone_number_limit = 0
        // };
        var form = {};

        $scope.updateForm = function() {
            form = $scope.form;
            console.log(form);
        };
    }]);
