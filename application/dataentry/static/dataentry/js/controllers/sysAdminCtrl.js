angular
    .module('DataEntry')
    .controller("sysAdminCtrl", function($scope) {

        // Variable Declarations
        var form = {
            address1_cutoff = 0,
            address1_limit = 0,
            address2_cutoff = 0,
            address2_limit = 0,
            person_cutoff = 0,
            person_limit = 0,
            phone_number_cutoff = 0,
            phone_number_limit = 0
        };
        // vm.address1_cutoff = 0;
        // vm.address1_limit = 0;
        // vm.address2_cutoff = 0;
        // vm.address2_limit = 0;
        // vm.person_cutoff = 0;
        // vm.person_limit = 0;
        // vm.phone_number_cutoff = 0;
        // vm.phone_number_limit = 0;

        // Function Declarations
        //vm.updateForm = updateForm;


        $scope.updateForm = function() {
            form = $scope.form;
            console.log(form);
        };
    });
