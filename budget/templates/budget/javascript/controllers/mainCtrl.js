angular
    .module('BudgetCalculation')
    .controller('MainCtrl', ['$scope','$http', '$location', '$window', 'mainCtrlService', function($scope, $http, $location, $window, mainCtrlService) {

            var vm = this;
            vm.form = {};

            vm.miscTotalValue = 0;
            vm.travelTotalValue = 0;
            vm.awarenessTotalValue = 0;
            vm.suppliesTotalValue = 0;

            vm.otherTravelTotalValue = [0];
            vm.otherMiscTotalValue = [0];
            vm.otherAwarenessTotalValue = [0];
            vm.otherSuppliesTotalValue = [0];

            vm.otherItemsTotals = [vm.otherTravelTotalValue,
                                    vm.otherMiscTotalValue,
                                    vm.otherAwarenessTotalValue,
                                    vm.otherSuppliesTotalValue];

            $scope.$on('handleOtherItemsTotalChangeBroadcast', function(event, args) {
                vm.otherItemsTotals[args['form_section']-1][0] = args['total'];
                vm.miscTotal();
                vm.travelTotal();
                vm.awarenessTotal();
                vm.suppliesTotal();
            });

            vm.salariesTotal = 0;
            $scope.$on('handleSalariesTotalChangeBroadcast', function(event, args) {
                vm.salariesTotal = args['total'];
            });



            /*vm.retrieveForm = function(id) {
                $http.get('/budget/api/budget_calculations/' + id + '/').
                        success(function (data) {
                            //We can reference the json object to fill our vm variables
                            vm.form = data;
                        console.log(data);
                        }).
                        error(function (data, status, headers, config) {
                            // called asynchronously if an error occurs
                            // or server returns response with an error status.
                        });
            };*/


            vm.foodAndShelterTotal = function() {
                return vm.foodTotal() + vm.shelterTotal();
            };
            vm.bunchTotal = function() {
                return  vm.commTotal() +
                        vm.travelTotalValue +
                        vm.adminTotal() +
                        vm.medicalTotal() +
                        vm.miscTotalValue +
                        vm.salariesTotal;
            };
            vm.stationTotal = function() {
                return  vm.foodAndShelterTotal() +
                        vm.bunchTotal() +
                        vm.awarenessTotalValue +
                        vm.suppliesTotalValue +
                        vm.salariesTotal;
            };

            //shelter

            vm.utilTotal = function() {
                return (vm.form.shelter_rent + vm.form.shelter_water + vm.form.shelter_electricity);
            };

            vm.shelterCheckboxTotal = function() {
                var totalAmount = 0;
                if (vm.form.shelter_shelter_startup) {
                    totalAmount += vm.form.shelter_shelter_startup_amount;
                }
                if (vm.form.shelter_shelter_two) {
                    totalAmount += vm.form.shelter_shelter_two_amount;
                }
                return totalAmount;
            };
            vm.shelterTotal = function () {
                return  vm.form.shelter_rent +
                        vm.form.shelter_water +
                        vm.form.shelter_electricity +
                        vm.shelterCheckboxTotal();
            };

            //Food and Gas Section

            vm.foodGasInterceptedGirls = function () {
                return  vm.form.food_and_gas_number_of_intercepted_girls_multiplier_before *
                        vm.form.food_and_gas_number_of_intercepted_girls *
                        vm.form.food_and_gas_number_of_intercepted_girls_multiplier_after;
            };
            vm.foodGasLimboGirls = function () {
                return  vm.form.food_and_gas_limbo_girls_multiplier *
                        vm.form.food_and_gas_number_of_limbo_girls *
                        vm.form.food_and_gas_number_of_days;
            };
            vm.foodTotal = function () {
                return vm.foodGasInterceptedGirls() + vm.foodGasLimboGirls();
            };

            //Communication Section
            vm.commManagerTotal = function () {
                var amount = 0;

                if (vm.form.communication_chair) {
                    amount += vm.form.communication_chair_amount;
                }
                if (vm.form.communication_manager) {
                    amount += vm.form.communication_manager_amount;
                }
                return amount;
            };

            vm.commNumberOfStaffTotal = function () {
                return  vm.form.communication_number_of_staff_with_walkie_talkies *
                        vm.form.communication_number_of_staff_with_walkie_talkies_multiplier;
            };

            vm.commEachStaffTotal = function () {
                return  vm.form.communication_each_staff *
                        vm.form.communication_each_staff_multiplier;
            };

            vm.commTotal = function () {
                return vm.commManagerTotal() + vm.commNumberOfStaffTotal() + vm.commEachStaffTotal();
            };

            //Misc Section
            vm.miscMaximum = function() {
                return vm.form.miscellaneous_number_of_intercepts_last_month * vm.form.miscellaneous_number_of_intercepts_last_month_multiplier;
            };
            vm.miscTotal = function() {
                vm.miscTotalValue = vm.miscMaximum() + vm.otherMiscTotalValue[0];
            };

            //Medical Section
            vm.medicalTotal = function() {
                return vm.form.medical_last_months_expense;
            };

            //Administration Section
            vm.adminStationaryTotal = function() {
                return (vm.form.administration_number_of_intercepts_last_month * vm.form.administration_number_of_intercepts_last_month_multiplier) + vm.form.administration_number_of_intercepts_last_month_adder;
            };
            vm.adminMeetingsTotal = function() {
                return vm.form.administration_number_of_meetings_per_month * vm.form.administration_number_of_meetings_per_month_multiplier;
            };
            vm.adminBoothRentalTotal = function() {
                var amount = 0;
                if(vm.form.administration_booth) {
                    amount += vm.form.administration_booth_amount;
                }
                if(vm.form.administration_registration) {
                    amount += vm.form.administration_registration_amount;
                }
                return amount;
            };
            vm.adminTotal = function() {
                return vm.adminStationaryTotal() + vm.adminMeetingsTotal() + vm.adminBoothRentalTotal();
            };

            //Travel Section
            vm.travelNumberOfStaffUsingBikesTotal = function() {
                return vm.form.travel_number_of_staff_using_bikes * vm.form.travel_number_of_staff_using_bikes_multiplier;
            };
            vm.travelMotorbikeOtherTotal = function() {
                var returnVal = 0;
                if(vm.form.travel_motorbike) {
                    returnVal = vm.form.travel_motorbike_amount;
                }
                return returnVal + vm.form.travel_plus_other;
            };
            vm.travelTotal = function() {
                var amount = 0;
                if(vm.form.travel_chair_with_bike) {
                    amount += vm.form.travel_chair_with_bike_amount;
                }
                if(vm.form.travel_manager_with_bike) {
                    amount += vm.form.travel_manager_with_bike_amount;
                }
                if(vm.form.travel_motorbike) {
                    amount += vm.form.travel_motorbike_amount;
                }
                vm.travelTotalValue = amount + vm.form.travel_plus_other + vm.form.travel_last_months_expense_for_sending_girls_home + (vm.form.travel_number_of_staff_using_bikes * vm.form.travel_number_of_staff_using_bikes_multiplier) + vm.otherTravelTotalValue[0];
            };

            //Supplies Section
            vm.suppliesTotal = function() {
                var amount = 0;
                if(vm.form.supplies_walkie_talkies_boolean) {
                    amount += vm.form.supplies_walkie_talkies_amount;
                }
                if(vm.form.supplies_recorders_boolean) {
                    amount += vm.form.supplies_recorders_amount;
                }
                if(vm.form.supplies_binoculars_boolean) {
                    amount += vm.form.supplies_binoculars_amount;
                }
                if(vm.form.supplies_flashlights_boolean) {
                    amount += vm.form.supplies_flashlights_amount;
                }
                vm.suppliesTotalValue = amount + vm.otherSuppliesTotalValue[0];
            };

            //Awareness Section
            vm.awarenessTotal = function() {
                var amount = 0;
                if(vm.form.awareness_contact_cards) {
                    amount += vm.form.awareness_contact_cards_amount;
                }
                if(vm.form.awareness_awareness_party_boolean) {
                    amount += vm.form.awareness_awareness_party;
                }
                if(vm.form.awareness_sign_boards_boolean) {
                    amount += vm.form.awareness_sign_boards;
                }
                vm.awarenessTotalValue = amount + vm.otherAwarenessTotalValue[0];
            };



        /*vm.deletePost = function(id) {
            mainCtrlService.deletePost(id);
        };*/


            /*vm.deletePost = function(id) {
                $http.delete('/budget/api/budget_calculations/' + id + '/').
                        success(function (data, status, headers, config) {
                            console.log("1");
                        }).
                        error(function (data, status, headers, config) {
                            console.log("2");
                            // called asynchronously if an error occurs
                            // or server returns response with an error status.
                        })
            };*/


        vm.updateForm = function() {
            mainCtrlService.updateForm(vm.form.id, vm.form).then(function(promise) {
                vm.id = promise.data.id;

                //Broadcast event to call the saveAllItems function in the otherItems controller
                $scope.$emit('handleBudgetCalcSavedEmit', {message: 'It is done.'});
                console.log("Test...");
                $window.location.assign('/budget/budget_calculations/money_distribution/view/0/');
            });
        };

            /*vm.updateForm = function() {
                $http.put('/budget/api/budget_calculations/' + vm.form.id + '/', vm.form)
                    .success(function(data, status) {
                        console.log("success");
                        vm.id = data.id;
                        //Broadcast event to call the saveAllItems function in the otherItems controller
                        $scope.$emit('handleBudgetCalcSavedEmit', {message: 'It is done.'});

                        $window.location.assign('/budget/budget_calculations');

                    })
                    .error(function(data, status) {
                        console.log("fail");
                    });
            };*/

        vm.createForm = function() {
            mainCtrlService.createForm(vm.form).then(function(promise) {
                var data = promise.data;
                vm.id = data.id;
                window.budget_calc_id = data.id;

                //Broadcast event to call the saveAllItems function in the otherItems controller
                $scope.$emit('handleBudgetCalcSavedEmit', {message: 'It is done.'});

                //TODO We should change this because this is bad
                $window.location.assign('/budget/budget_calculations/money_distribution/view/0/');
            });
        };

            /*vm.createForm = function() {
                $http.post('/budget/api/budget_calculations/', vm.form)
                    .success(function(data, status) {
                        console.log("success Create");
                        vm.id = data.id;
                        window.budget_calc_id = data.id;
                        //Broadcast event to call the saveAllItems function in the otherItems controller
                        $scope.$emit('handleBudgetCalcSavedEmit', {message: 'It is done.'});


                        $window.location.assign('/budget/budget_calculations');

                    })
                    .error(function(data, status) {
                        console.log("fail create");
                    });

            };*/

            vm.retrieveForm = function(id) {
                mainCtrlService.retrieveForm(id).then(function(promise){
                    vm.form = promise.data;
                });
            };

            vm.retrieveNewForm = function() {
                mainCtrlService.retrieveNewForm(window.budget_calc_id).then(function(promise){
                    var data = promise.data.budget_form;
                    data.members = [];
                    data.id = undefined;
                    vm.form = data;
                })
            };


            if( (window.submit_type) == 1 ) {
                vm.create = true;
                vm.form.border_station = window.budget_calc_id;
                vm.retrieveNewForm();
            }
            else if( (window.submit_type) == 2)  {
                vm.update = true;
                vm.retrieveForm(window.budget_calc_id);
            }
            else if( (window.submit_type) == 3) {
                vm.view = true;
                $('input').prop('disabled', true);
                console.log(window.budget_calc_id);
                vm.retrieveForm(window.budget_calc_id);
            }

        }]);