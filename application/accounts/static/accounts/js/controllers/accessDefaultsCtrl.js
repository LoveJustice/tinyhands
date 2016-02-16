angular
    .module('AccountsMod')
    .controller('AccessDefaultsCtrl', ['$window','PermissionsSets','$timeout',function($window, PermissionsSets, $timeout) {
        var vm = this;
        vm.saveButtonText = "Save All";
        vm.saveButtonColor = "btn-success";
        vm.activate = function () {
          vm.permissionsSets = [];
          vm.nameError = false;
          $window.onbeforeunload = function(event) {
              var unsavedChanges = false;

              vm.permissionsSets.forEach( function (elm, idx) {
                if (elm.is_new) {
                  unsavedChanges = true;
                }
              })

              if(unsavedChanges) {
                  return "You have unsaved changes.";
              }
              return;
          };

          PermissionsSets.all().$promise.then(function(response) {
            vm.permissionsSets = response.results;
          });
        }

        vm.delete = function(permissionSetIndex) {
            var permissionsSet = vm.permissionsSets[permissionSetIndex];
            if (permissionsSet.is_used_by_accounts) return;
            if(permissionsSet.is_new) {
                vm.permissionsSets.splice(permissionSetIndex, 1);
            }else {
                PermissionsSets.destroy({id: permissionsSet.id}).$promise.then(function() {
                    vm.permissionsSets.splice(permissionSetIndex, 1);
                });
            }
        }

        vm.addAnother = function() {
            vm.permissionsSets.push({
                is_new: true,
                is_used_by_accounts: false,
                name: "",
                permission_accounts_manage: false,
                permission_border_stations_add: false,
                permission_border_stations_delete: false,
                permission_border_stations_edit: false,
                permission_border_stations_view: false,
                permission_budget_manage: false,
                permission_irf_add: false,
                permission_irf_delete: false,
                permission_irf_edit: false,
                permission_irf_view: false,
                permission_receive_email: false,
                permission_vdc_manage: false,
                permission_vif_add: false,
                permission_vif_delete: false,
                permission_vif_edit: false,
                permission_vif_view: false
            });
        }
        vm.saveAll = function() {
            vm.swapSaveButton("Saving...", "btn-primary");
            vm.nameError = false;
            for(var i = 0; i<vm.permissionsSets.length; i++) {
                saveSet(i);
            }
            timeout = $timeout(function() {
                vm.swapSaveButton("Saved", "btn-primary");
                timeout = $timeout(function() {vm.swapSaveButton("Save All", "btn-success")}, 750);
            }, 750);
        }

        vm.swapSaveButton = function(text, color) {
            vm.saveButtonText = text;
            vm.saveButtonColor = color;
        }

        function saveSet(index) {
            var permissionsSet = vm.permissionsSets[index];
            var call = null;
            if(permissionsSet.is_new) {
                call = PermissionsSets.create(permissionsSet).$promise
            }else {
                call = PermissionsSets.update(permissionsSet).$promise;
            }
            call.then(function(data){
                vm.permissionsSets[index] = data;
            }, function(error) { // catch name error
                vm.nameError = true;
                permissionsSet.nameError = true;
            });
        }

        vm.activate();

    }]);
