angular
    .module('AccountsMod')
    .controller('AccountsCtrl', ['Accounts','PermissionsSets', '$modal', function(Accounts, PermissionsSets, $modal) {
        var vm = this;

        vm.accounts = Accounts.all();
        vm.permissions = PermissionsSets.all();
        vm.currentuser = Accounts.me();
        vm.update = Accounts.update();

        vm.resendActivationEmail = function(account) {
          Accounts.resendActivationEmail({id:account.id});
        };

        vm.openModal = function(account) {
          var user_name = account.first_name+" "+account.last_name;
          var deleteModal = $modal.open({
            templateUrl: 'modal.html',
            controller: 'ModalCtrl',
            controllerAs: 'modalCtrl',
            resolve: {
              user_name: function () {
                return user_name;
              }
            }
          });
          deleteModal.result.then( function () {
            Accounts.destroy({id:account.id}).$promise.then( function () {
              vm.accounts = Accounts.all();
            })
          })
        }


    }]);
