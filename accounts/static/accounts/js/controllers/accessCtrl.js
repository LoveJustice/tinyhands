angular
    .module('AccountsMod')
    .controller('AccessCtrl', ['Accounts','PermissionsSets', function(Accounts, PermissionsSets) {
        var vm = this;

        vm.accounts = Accounts.all();
        vm.permissions = PermissionsSets.all();
        vm.foo = "testing";
        //Whenever permissionText is changed, then grab the appropriate permissionsSet and set each button value to that


         vm.changeUserRole = function(account){
            PermissionsSets.get({id:account.user_designation}).$promise.then(function (permissions) {
                account.permission_irf_view=  permissions.permission_irf_view;
                account.permission_irf_add = permissions.permission_irf_add;
                account.permission_irf_edit = permissions.permission_irf_edit;
                account.permission_irf_delete = permissions.permission_irf_delete;
                account.permission_vif_view = permissions.permission_vif_view;
                account.permission_vif_add = permissions.permission_vif_add;
                account.permission_vif_edit = permissions.permission_vif_edit;
                account.permission_vif_delete = permissions.permission_vif_delete;
                account.permission_border_stations_view = permissions.permission_border_stations_view;
                account.permission_border_stations_add = permissions.permission_border_stations_add;
                account.permission_border_stations_edit = permissions.permission_border_stations_edit;
                account.permission_border_stations_delete = permissions.permission_border_stations_delete;
                account.permission_accounts_manage = permissions.permission_accounts_manage;
                account.permission_receive_email = permissions.permission_receive_email;
                account.permission_vdc_manage = permissions.permission_vdc_manage;
                account.permission_budget_manage = permissions.permission_budget_manage;
            });  
        }
    }]);