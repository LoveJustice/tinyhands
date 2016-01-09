angular
    .module('BudgetCalculation')
    .controller('otherBudgetItemsCtrl', ['$scope','$http', 'otherItemsService', function($scope, $http, otherItemsService) {
        var vm = this;

        // Variable Declarations
        var idCounter = 0;
        $scope.form_section = 0;
        vm.budget_item_parent = 0;

        vm.formsList = [];
        vm.miscForms = [];
        vm.travelForms = [];
        vm.awarenessForms = [];
        vm.suppliesForms = [];
        vm.shelterForms = [];
        vm.staffForms = [];
        vm.foodGasForms = [];
        vm.communicationForms = [];
        vm.formsList.push(vm.travelForms, vm.miscForms, vm.awarenessForms, vm.suppliesForms, vm.shelterForms,  vm.foodGasForms, vm.communicationForms, vm.staffForms);


        // Functions Definitions
        vm.addNewItem = addNewItem;
        vm.otherItemsTotal = otherItemsTotal;
        vm.removeItem = removeItem;
        vm.retrieveForm = retrieveForm;
        vm.retrieveNewForm = retrieveNewForm;
        vm.saveAllItems = saveAllItems;

        // Event Listeners
        $scope.$on('handleBudgetCalcSavedBroadcast', function() {
            saveAllItems();
        });

        // Calling the main function
        main();

        // Function Implementations
        function main(){
            if( window.submit_type == 1 ) {
                vm.retrieveNewForm();
            }
            else if( window.submit_type == 2)  {
                // edit strategy
                vm.retrieveForm(window.budget_calc_id);
                vm.budget_item_parent = window.budget_calc_id;
            }
            else {
                //viewing or something else
                vm.retrieveForm(window.budget_calc_id);
            }
        }

        function retrieveForm(id) {
            // grab all of the otherBudgetItems for this budgetCalcSheet
            otherItemsService.retrieveForm(id)
                .then(function (promise) {
                    var data = promise.data;
                    for( var x = 0; x < data.length; x++ ){
                        if (data[x].form_section === $scope.form_section){
                            vm.formsList[$scope.form_section-1].push(data[x]);
                        }
                    }
                    vm.otherItemsTotal();
                });
        }

        function retrieveNewForm() {
            otherItemsService.retrieveNewForm(window.budget_calc_id).then(function(promise){
                var itemsList = promise.data.other_items;
                for(var x = 0; x < itemsList.length; x++){
                    if (itemsList[x].form_section === $scope.form_section){
                        itemsList[x].id = -1;
                        vm.formsList[$scope.form_section-1].push(itemsList[x]);
                    }
                }
                vm.otherItemsTotal();
            });
        }

        function addNewItem(){
            idCounter--;
            vm.formsList[$scope.form_section-1].push(
                    {
                        id: idCounter,
                        name: '',
                        cost: 0,
                        form_section: $scope.form_section,
                        budget_item_parent: vm.budget_item_parent
                    });
        }

        function removeItem(itemId, index){
            if(itemId>-1){
                otherItemsService.removeItem(itemId);
            }
            vm.formsList[$scope.form_section-1].splice(index, 1); // Remove item from the list
            otherItemsTotal();
        }

        function saveAllItems(){
            var item = {};
            for(var list = 0; list < vm.formsList.length; list++){
                for(var itemIndex = 0; itemIndex < vm.formsList[list].length; itemIndex++){
                    item = vm.formsList[list][itemIndex];
                    if(item.id < 0){
                        saveItem(item);
                    }else{
                        updateItem(item);
                    }
                }
            }
        }

        function saveItem(item){
            otherItemsService.saveItem(item);
        }

        function updateItem(item){
            otherItemsService.updateItem(item);
        }

        function otherItemsTotal(){
            var acc =0;
            for(var x = 0; x < vm.formsList[$scope.form_section-1].length; x++){
                acc += vm.formsList[$scope.form_section-1][x].cost;
            }
            $scope.miscItemsTotalVal = acc;
            $scope.$emit('handleOtherItemsTotalChangeEmit', {form_section: $scope.form_section, total: acc});
        }
    }]);
