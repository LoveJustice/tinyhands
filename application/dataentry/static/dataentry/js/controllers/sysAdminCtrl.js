angular
    .module('SysAdminSettings')
    .controller("sysAdminCtrl", ['$scope', function($scope){
        var vm = this;

        // vm.form = {};
        vm.location_value = location_value;

        function getLocationValue() {
            return vm.location_value;
        }
    }]);
