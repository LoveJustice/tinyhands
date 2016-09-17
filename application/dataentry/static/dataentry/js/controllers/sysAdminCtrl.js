'use strict';

angular
    .module('DataEntry')
    .controller("sysAdminCtrl", ['$scope', '$http', '$window', 'sysAdminService', function($scope, $http, $window, sysAdminService) {
        var vm = this;

        vm.form = {};


        vm.activate = function() {
            sysAdminService.retrieveForm().then(function(promise){
                vm.form = vm.transformDataFromApi(promise.data);
            });
        };

        vm.transformDataFromApi = function (data) {
            var localData = angular.copy(data.data);
            var serializedObject = angular.copy(data);
            var settingNames = [];
            for (var x = 0; x < localData.length; x++){
                var setting = localData[x];
                serializedObject[setting.name] = {value: setting.value, description: setting.description};
                settingNames.push(setting.name);
            }
            delete serializedObject.data;
            serializedObject.settingNames = settingNames;
            console.log(serializedObject);
            return serializedObject;
        };

        vm.transformToApiData = function (data) {
            var settings = [];
            data.settingNames.forEach(function (settingName) {
                var setting = data[settingName];
                settings.push({name: settingName, value: setting.value, description: setting.description});
                delete data[settingName];
            });
            delete data.settingNames;
            data.data = settings;
            return data;
        };

        vm.updateForm = function() {
            sysAdminService.updateForm(vm.transformToApiData(vm.form)).then(function(promise){
                vm.form = vm.transformDataFromApi(promise.data);
                $window.location.assign('/data-entry/sysadminsettings/1/');
            });
        };

        vm.activate();
    }]);
