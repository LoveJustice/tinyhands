angular
    .module('AccountsMod')
    .controller('AccountsCtrl', ['Accounts','PermissionsSets', '$modal', function(Accounts, PermissionsSets, $modal) {
        var vm = this;

        vm.activate = function () {
            vm.sortColumn = 'email';
            vm.accounts = Accounts.all();
            PermissionsSets.all().$promise.then(vm.createPermissionsArray);
            vm.currentuser = Accounts.me();
            vm.permissions = PermissionsSets.all();
            vm.permissionsDesignations = {};
            vm.sorticon = "/static/images/sortIcon.jpg";
            vm.reverse = '-';
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
           loop through permission set and make entries with designation id as key, designation name as value
           ex: permissionsSet[1] = Super Administrator */
        vm.createPermissionsArray = function(permissionSet) {

            for (i=0; i < permissionSet.count; i++){
                vm.permissionsDesignations[permissionSet.results[i].id] = permissionSet.results[i].name;
            }
        }

        vm.designationFinder = function(userDesignation) {
            return vm.permissionsDesignations[userDesignation];
        }

        vm.reversefunc = function() {
            if (vm.reverse === '+')
                vm.reverse = '-';
            else
                vm.reverse = '+';
        }

        vm.sortIcon = function(column, name){
            if(name === vm.sortColumn){
                switch (column) {
                    case "number":
                        return vm.reverse == '-' ? "glyphicon-sort-by-order-alt" : "glyphicon-sort-by-order";
                    case "letter":
                        return vm.reverse == '-' ? "glyphicon-sort-by-alphabet-alt" : "glyphicon-sort-by-alphabet";
                    default:
                        return "glyphicon-sort";
                }
            }
            return "glyphicon-sort";
        }

        vm.activate();
    }]);
