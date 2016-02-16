angular
    .module('AccountsMod')
    .controller('AccountsCtrl', ['Accounts','PermissionsSets', '$modal', function(Accounts, PermissionsSets, $modal) {
        var vm = this;

        vm.activate = function () {
          vm.accounts = Accounts.all();
          PermissionsSets.all().$promise.then(vm.createPermissionsArray);
          vm.currentuser = Accounts.me();
          vm.permissionsDesignations = {};
        }

        vm.resendActivationEmail = function(accountID) {
          Accounts.resendActivationEmail({id:accountID});
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

        /* Created associative array to make referencing designation names faster
           loop through permission set and create associative array with designation id as key, designation name as value
           ex: permissionsSet[1] = Super Administrator */
        vm.createPermissionsArray = function(permissionSet) {

            for (i=0; i < permissionSet.count; i++){
                vm.permissionsDesignations[permissionSet.results[i].id] = permissionSet.results[i].name;
            }
        }

        vm.designationFinder = function(userDesignation) {
            return vm.permissionsDesignations[userDesignation];
        }

        vm.activate();

    }]);
