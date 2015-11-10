angular
    .module('AccountsMod')
    .controller('ModalCtrl', function($scope, $modalInstance, user_name) {
        var vm = this;

        $scope.user_name = user_name;

        vm.delete = function() {
          $modalInstance.close(true);
        };
        vm.cancel = function () {
          $modalInstance.dismiss("cancel");
        };
    });
