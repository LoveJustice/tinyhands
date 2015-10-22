'use strict';

angular
    .module('AccountsMod')
    .controller('EditAccountCtrl', EditAccountCtrl)

    EditAccountCtrl.$inject = ['Accounts', 'PermissionsSets']

    function EditAccountCtrl(Accounts, PermissionsSets) {
        var vm = this;
        window.foo = vm;
        vm.foo = "Hello"

        vm.account = {};
        vm.permissionsSets = PermissionsSets.all();

    }
