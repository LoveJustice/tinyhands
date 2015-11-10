angular
    .module('AccountsMod')
    .controller('ModalCtrl', function($scope, $modalInstance) {
        var vm = this;

        vm.delete = function() {
          $modalInstance.close(true);
        };
        vm.cancel = function () {
          $modalInstance.dismiss("cancel");
        };
    });
