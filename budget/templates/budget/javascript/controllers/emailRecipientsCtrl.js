angular
    .module('BudgetCalculation')
    .controller("emailRecipientsCtrl", ['$window', '$scope','$http', 'emailRecipientsService', function($window, $scope, $http, emailRecipientsService) {
        var vm = this;
        vm.staff = {};
        vm.committeeMembers = {};
        vm.loading = false;

        //function definitions
        vm.sendEmails = sendEmails;
        vm.retrieveForm = retrieveForm;

        function main(){
            vm.retrieveForm();
        }
        main();


        function retrieveForm() {
            emailRecipientsService.retrieveForm().then(function(promise){
                var data = promise.data;
                vm.committeeMembers = data.committee_members;
                vm.staff = data.staff_members;
            });
        }

        function sendEmails(){
            vm.loading = true;
            var people = {};
            people.budget_calc_id = window.pk;
            people.staff_ids = [];
            people.committee_ids = [];

            for(var x = 0; x<vm.staff.length; x++){
                if (vm.staff[x].receives_money_distribution_form){
                    people.staff_ids.push(vm.staff[x].id);
                }
            }
            for(x=0; x<vm.committeeMembers.length; x++){
                if (vm.committeeMembers[x].receives_money_distribution_form){
                    people.committee_ids.push(vm.committeeMembers[x].id);
                }
            }
            emailRecipientsService.sendEmails(people).then(function(){
                vm.loading = false;
                $window.location.assign('/');
            });
        }
    }]);