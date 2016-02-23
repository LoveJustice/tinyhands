angular
    .module('DataEntry')
    .controller("sysAdminCtrl", ['$scope', function($scope){
        var vm = this;

        vm.form = {};

        vm.locationTotal = function() {
            return vm.form.location_value;
        }
    }]);
