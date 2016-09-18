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
        return $http.get('/api/site-settings/')
            .success(function(data) {
                return data;
            })
            .error(function(data, status) {
                console.log(data, status);
            });
    }

    function updateForm(form) {
        return $http.put('/api/site-settings/' + form.id + '/', form)
            .success(function(data) {
                return data;
            })
            .error(function(data, status) {
                console.log(data, status);
            });
    }

}
