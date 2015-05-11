// service
angular
    .module('BudgetCalculation')
    .factory('emailRecipientsService', emailRecipientsService);

emailRecipientsService.$inject = ['$http', '$q'];

function emailRecipientsService($http) {
    return {
        retrieveForm: retrieveForm,
        sendEmails: sendEmails
    };

    function retrieveForm() {
        return $http.get('/budget/api/budget_calculations/money_distribution/' + window.border_station + '/')
            .success(function (data) {
                return data;
            })
            .error(function (data, status, headers, config) {
            });
    }

    function sendEmails(people) {
        return $http.post('/budget/api/budget_calculations/money_distribution/0/', people)
            .success(function () {
                console.log("success!");
                return true;
            })
            .error(function (data, status) {
                console.log("failure to send emails!");
                console.log(data, status);
            });
    }

}
