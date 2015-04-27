angular
    .module('BudgetCalculation')
    .controller('otherBudgetItemsCtrl', ['$scope','$http', '$location', '$window', function($scope, $http, $location, $window) {
        var idCounter = 0;
        var vm = this;

        $scope.form_section = 0;

        vm.formsList = [];
        vm.miscForms = [];
        vm.travelForms = [];
        vm.awarenessForms = [];
        vm.suppliesForms = [];

        vm.formsList.push(vm.travelForms, vm.miscForms, vm.awarenessForms, vm.suppliesForms);

        vm.budget_item_parent = 0;


        // functions for the controller
        vm.addNewItem = addNewItem;
        vm.retrieveForm = retrieveForm;
        vm.removeItem = removeItem;
        vm.saveAllItems = saveAllItems;
        vm.otherItemsTotal = otherItemsTotal;

        main();

        $scope.$on('handleBudgetCalcSavedBroadcast', function(event, args) {
            saveAllItems();
        });

        function main(){
            if( window.submit_type == 1 ) {
                //creation strategy
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
            $http.get('/budget/api/budget_calculations/items_detail/' + id + '/').
                    success(function (data) {
                        for( var x = 0; x < data.length; x++ ){
                            if (data[x].form_section === $scope.form_section){
                                vm.formsList[$scope.form_section-1].push(data[x]);
                            }
                        }
                        vm.otherItemsTotal();
                    }).
                    error(function (data, status, headers, config) {
                        console.log(data, status, headers, config);
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
                $http.delete('/budget/api/budget_calculations/items_detail/' + itemId + '/').
                    success(function (data) {
                        console.log("successfully deleted");
                    }).
                    error(function (data, status, headers, config) {
                        console.log(data, status, headers, config);
                    });
            }
            vm.formsList[$scope.form_section-1].splice(index, 1); // Remove item from the list
            otherItemsTotal();
        }

        function saveAllItems(){
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
            item.budget_item_parent = window.budget_calc_id;
            $http.post('/budget/api/budget_calculations/items_list/', item)
                    .success(function(data, status) {
                        item.id = data.id;
                    })
                    .error(function(data, status){
                        console.log("failure to create budget item!");
                    });
        }

        function updateItem(item){
            $http.put('/budget/api/budget_calculations/items_detail/' + item.id + '/', item)
                    .success(function(data, status) {
                        console.log("success");
                    })
                    .error(function(data, status) {
                        console.log("failure to update budget item!");
                    });
        }

        function otherItemsTotal(){
            var acc =0;
            for(var x = 0; x < vm.formsList[$scope.form_section-1].length; x++){
                acc += vm.formsList[$scope.form_section-1][x].cost;
            }
            $scope.miscItemsTotalVal = acc;
            $scope.$emit('handleOtherItemsTotalChangeEmit', {form_section: $scope.form_section, total: acc});
        }


    }])