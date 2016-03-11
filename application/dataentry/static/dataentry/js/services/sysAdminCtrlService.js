angular
    .module('DataEntry')
    .factory('sysAdminCtrlService', sysAdminCtrlService);

sysAdminCtrlService.$inject = ['$http'];

function sysAdminCtrlService($http) {
    return {
        retrieveForm: retrieveForm,
        updateForm: updateForm
	};

    function retrieveForm(form) {
        console.log("retrieveForm");
        return $http.get('/data-entry/api/sysadminsettings/1/', form)
            .success(function(data) {
                return data;
            })
            .error(function(data, status) {
                console.log(data, status);
            });
    }

    function updateForm(form) {
        console.log("updateForm");
        return $http.put('/data-entry/api/sysadminsettings/1/', form)
            .success(function(data) {
                return data;
            })
            .error(function(data, status) {
                console.log(data, status);
            });
    }

}
