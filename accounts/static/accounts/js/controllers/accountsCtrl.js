angular
    .module('AccountsMod')
    .controller('AccountsCtrl', ['Accounts','PermissionsSets', '$modal', function(Accounts, PermissionsSets, $modal) {
        var vm = this;

        vm.accounts = Accounts.all();
        vm.permissions = PermissionsSets.all();
        vm.currentuser = Accounts.me();
        vm.update = Accounts.update();

        vm.openModal = function(account) {
          var deleteModal = $modal.open({
            templateUrl: 'modal.html',
            controller: 'ModalCtrl',
            controllerAs: 'modalCtrl'
          });
          deleteModal.result.then( function () {
            Accounts.destroy({id:account.id}).$promise.then( function () {
              vm.accounts = Accounts.all();
            })
          })
        }


    }]);
