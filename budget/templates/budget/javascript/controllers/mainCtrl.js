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


            // Budget Calc sheets are for the 15th of every month
            vm.date = new Date();
            vm.date.setDate(15);

            vm.otherItemsTotals = [vm.otherTravelTotalValue,
                                    vm.otherMiscTotalValue,
                                    vm.otherAwarenessTotalValue,
                                    vm.otherSuppliesTotalValue];

            $scope.$on('handleOtherItemsTotalChangeBroadcast', function(event, args) {
                vm.otherItemsTotals[args['form_section']-1][0] = args['total'];
                callTotals();
            });

            function callTotals (){
                vm.miscTotal();
                vm.travelTotal();
                vm.awarenessTotal();
                vm.suppliesTotal();
            }

            vm.salariesTotal = 0;
            $scope.$on('handleSalariesTotalChangeBroadcast', function(event, args) {
                vm.salariesTotal = args['total'];
            });

            $scope.$on('lastBudgetTotalBroadcast', function(event, args) {
                console.log(args);
                vm.last_months_total_cost = args['total'];
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


        vm.updateForm = function() {
            mainCtrlService.updateForm(vm.form.id, vm.form).then(function(promise) {
                vm.id = promise.data.id;
                console.log(vm.id);
                //Broadcast event to call the saveAllItems function in the otherItems controller
                $scope.$emit('handleBudgetCalcSavedEmit', {message: 'It is done.'});
                console.log("Test...");
                $window.location.assign('/budget/budget_calculations/money_distribution/view/' + vm.id + '/');
            });
        };


        vm.createForm = function() {
            mainCtrlService.createForm(vm.form).then(function(promise) {
                var data = promise.data;
                vm.id = data.id;
                window.budget_calc_id = data.id;

                //Broadcast event to call the saveAllItems function in the otherItems controller
                $scope.$emit('handleBudgetCalcSavedEmit', {message: 'It is done.'});

                $window.location.assign('/budget/budget_calculations/money_distribution/view/' + vm.id + '/');
            });
        };


        vm.retrieveForm = function(id) {
            mainCtrlService.retrieveForm(id).then(function(promise){
                vm.form = promise.data;
                vm.form.month_year = new Date(promise.data.month_year);
                $scope.$emit('dateSetEmit', {date: vm.form.month});
            });
        };


        vm.retrieveNewForm = function() {
            mainCtrlService.retrieveNewForm(window.budget_calc_id).then(function(promise){
                var data = promise.data.budget_form;
                if (promise.data.None){
                    resetValuesToZero();
                }
                else{
                    vm.form = data;
                }

                vm.form.month_year = vm.date;
                data.members = [];
                data.id = undefined;
            })
        };


        function resetValuesToZero() {
            vm.form = {
                shelter_shelter_startup_amount: 71800,
                shelter_shelter_two_amount: 36800,
                communication_chair: false,
                communication_chair_amount: 0,
                communication_manager: false,
                communication_manager_amount: 0,
                communication_number_of_staff_with_walkie_talkies: 0,
                communication_number_of_staff_with_walkie_talkies_multiplier: 0,
                communication_each_staff: 0,
                communication_each_staff_multiplier: 0,
                travel_chair_with_bike: false,
                travel_chair_with_bike_amount: 0,
                travel_manager_with_bike: false,
                travel_manager_with_bike_amount: 0,
                travel_number_of_staff_using_bikes: 0,
                travel_number_of_staff_using_bikes_multiplier: 0,
                travel_last_months_expense_for_sending_girls_home: 0,
                travel_motorbike: false,
                travel_motorbike_amount: 0,
                travel_plus_other: 0,
                administration_number_of_intercepts_last_month: 0,
                administration_number_of_intercepts_last_month_multiplier: 0,
                administration_number_of_intercepts_last_month_adder: 0,
                administration_number_of_meetings_per_month: 0,
                administration_number_of_meetings_per_month_multiplier: 0,
                administration_booth: false,
                administration_booth_amount: 0,
                administration_registration: false,
                administration_registration_amount: 0,
                medical_last_months_expense: 0,
                miscellaneous_number_of_intercepts_last_month: 0,
                miscellaneous_number_of_intercepts_last_month_multiplier: 0,
                shelter_rent: 0,
                shelter_water: 0,
                shelter_electricity: 0,
                shelter_shelter_startup: false,
                shelter_shelter_two: false,
                food_and_gas_number_of_intercepted_girls: 0,
                food_and_gas_number_of_intercepted_girls_multiplier_before: 0,
                food_and_gas_number_of_intercepted_girls_multiplier_after: 0,
                food_and_gas_limbo_girls_multiplier: 0,
                food_and_gas_number_of_limbo_girls: 0,
                food_and_gas_number_of_days: 0,
                awareness_contact_cards: false,
                awareness_contact_cards_boolean_amount: 0,
                awareness_contact_cards_amount: 0,
                awareness_awareness_party_boolean: false,
                awareness_awareness_party: 0,
                awareness_sign_boards_boolean: false,
                awareness_sign_boards: 0,
                supplies_walkie_talkies_boolean: false,
                supplies_walkie_talkies_amount: 0,
                supplies_recorders_boolean: false,
                supplies_recorders_amount: 0,
                supplies_binoculars_boolean: false,
                supplies_binoculars_amount: 0,
                supplies_flashlights_boolean: false,
                supplies_flashlights_amount: 0
            }
        }

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
