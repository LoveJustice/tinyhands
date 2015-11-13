angular
    .module('AccountsMod')
    .controller('AccessDefaultsCtrl', ['$window','PermissionsSets',function($window, PermissionsSets) {
        var vm = this;
        vm.permissionsSets = [];
        
        $window.onbeforeunload = function(event) {
            var unsavedChanges = false;
            for(var i = 0; i < vm.permissionsSets.length; i++) {
                if(vm.permissionsSets[i].is_new) {
                    unsavedChanges = true;
                    break;
                }
            }
            if(unsavedChanges) {
                return "You have unsaved changes.";            
            }
        };
		
        PermissionsSets.all().$promise.then(function(response) {
			vm.permissionsSets = response.results;
		});
        
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
            for(var i = 0; i<vm.permissionsSets.length; i++) {
                var permissionsSet = vm.permissionsSets[i];
                if(permissionsSet.is_new) {
                    PermissionsSets.create(permissionsSet);
                }else {
                    PermissionsSets.update(permissionsSet);
                }
            }
        }

    }]);
