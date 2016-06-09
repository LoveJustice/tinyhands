angular
    .module('DataEntry')
    .factory('sysAdminService', sysAdminService);

sysAdminService.$inject = ['$http'];

function sysAdminService($http) {
    return {
        retrieveForm: retrieveForm,
        updateForm: updateForm
	};

    function retrieveForm() {
        return $http.get('/data-entry/api/sysadminsettings/1/')
            .success(function(data) {
                return data;
            })
            .error(function(data, status) {
                console.log(data, status);
            });
    }

    function updateForm(form) {
        return $http.put('/data-entry/api/sysadminsettings/1/', form)
            .success(function(data) {
                return data;
            })
            .error(function(data, status) {
                console.log(data, status);
            });
    }

}
