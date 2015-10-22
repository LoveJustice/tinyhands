angular
    .module('AccountsMod')
    .controller('AccountsCtrl', ['Accounts','PermissionsSets', function(Accounts, PermissionsSets) {
        var vm = this;

        vm.accounts = Accounts.all();
        vm.permissions = PermissionsSets.all();
        vm.foo = "testing";

    }]);
