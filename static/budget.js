function budgetViewModel() {
    //Medical Section
    this.medicalExpense = ko.observable(0);
    this.medicalTotal = ko.computed(function() {
        return parseFloat(this.medicalExpense());
    }, this);

    //Administration Section
    this.adminNumberOfInterceptionsLastMonth = ko.observable(0);
    this.adminNumberOfInterceptionsLastMonthMultiplier = ko.observable(20);
    this.adminNumberOfInterceptionsLastMonthAdder = ko.observable(1000);
    this.adminNumberOfMeetingsPerMonth = ko.observable(0);
    this.adminNumberOfMeetingsPerMonthMultiplier = ko.observable(600);
    this.adminBoothBool = ko.observable(false);
    this.adminBoothAmount = ko.observable(30000);
    this.adminRegistrationBool = ko.observable(false);
    this.adminRegistrationAmount = ko.observable(2000);
    this.adminStationaryTotal = ko.computed(function() {
        return (parseFloat(this.adminNumberOfInterceptionsLastMonth()) * parseFloat(this.adminNumberOfInterceptionsLastMonthMultiplier())) + parseFloat(this.adminNumberOfInterceptionsLastMonthAdder());
    }, this);
    this.adminMeetingsTotal = ko.computed(function() {
        return parseFloat(this.adminNumberOfMeetingsPerMonth()) * parseFloat(this.adminNumberOfMeetingsPerMonthMultiplier());
    }, this);
    this.adminBoothRentalTotal = ko.computed(function() {
        var amount = 0;
        if(this.adminBoothBool()) {
            amount += parseFloat(this.adminBoothAmount());
        }
        if(this.adminRegistrationBool()) {
            amount += parseFloat(this.adminRegistrationAmount());
        }
        return amount;
    }, this);
    this.adminTotal = ko.computed(function() {
        return parseFloat(this.adminStationaryTotal()) + parseFloat(this.adminMeetingsTotal()) + parseFloat(this.adminBoothRentalTotal());
    }, this);

    //Travel Section
    this.travelChairWithBikeBool = ko.observable(false);
    this.travelChairWithBikeAmount = ko.observable(2000);
    this.travelManagerWithBikeBool = ko.observable(false);
    this.travelManagerWithBikeAmount = ko.observable(2000);
    this.travelNumberOfStaffUsingBikes = ko.observable(0);
    this.travelNumberOfStaffUsingBikesMultiplier = ko.observable(1000);
    this.travelSendingGirlsHomeExpense = ko.observable(0);
    this.travelMotorbikeBool = ko.observable(false);
    this.travelMotorbikeAmount = ko.observable(0);
    this.travelOther = ko.observable(0);
    this.travelTotal = ko.computed(function() {
        var amount = 0;
        if(this.travelChairWithBikeBool()) {
            amount += parseFloat(this.travelChairWithBikeAmount());
        }
        if(this.travelManagerWithBikeBool()) {
            amount += parseFloat(this.travelManagerWithBikeAmount());
        }
        if(this.travelMotorbikeBool()) {
            amount += parseFloat(this.travelMotorbikeAmount());
        }
        return amount + parseFloat(this.travelOther()) + parseFloat(this.travelSendingGirlsHomeExpense()) +
            (parseFloat(this.travelNumberOfStaffUsingBikes()) * parseFloat(this.travelNumberOfStaffUsingBikesMultiplier()));

    }, this);

    //Supplies Section
    this.suppliesWalkieTalkiesBool = ko.observable(false);
    this.suppliesWalkieTalkiesAmount = ko.observable(0);
    this.suppliesRecordersBool = ko.observable(false);
    this.suppliesRecordersAmount = ko.observable(0);
    this.suppliesBinocularsBool = ko.observable(false);
    this.suppliesBinocularsAmount = ko.observable(0);
    this.suppliesFlashlightsBool = ko.observable(false);
    this.suppliesFlashlightsAmount = ko.observable(0);
    this.suppliesTotal = ko.computed(function() {
        var amount = 0;
        if(this.suppliesWalkieTalkiesBool()) {
            amount += parseFloat(this.suppliesWalkieTalkiesAmount());
        }
        if(this.suppliesRecordersBool()) {
            amount += parseFloat(this.suppliesRecordersAmount());
        }
        if(this.suppliesBinocularsBool()) {
            amount += parseFloat(this.suppliesBinocularsAmount());
        }
        if(this.suppliesFlashlightsBool()) {
            amount += parseFloat(this.suppliesFlashlightsAmount());
        }
        return amount;
    }, this);

    //Awareness Section
    this.awarenessContactCardsBool = ko.observable(false);
    this.awarenessContactCardsAmount = ko.observable(4000);
    this.awarenessAwarenessPartyBool = ko.observable(false);
    this.awarenessAwarenessPartyAmount = ko.observable(0);
    this.awarenessSignBoardsBool = ko.observable(false);
    this.awarenessSignBoardsAmount = ko.observable(0);
    this.awarenessTotal = ko.computed(function() {
        var amount = 0;
        if(this.awarenessContactCardsBool()) {
            amount += parseFloat(this.awarenessContactCardsAmount());
        }
        if(this.awarenessAwarenessPartyBool()) {
            amount += parseFloat(this.awarenessAwarenessPartyAmount());
        }
        if(this.awarenessSignBoardsBool()) {
            amount += parseFloat(this.awarenessSignBoardsAmount());
        }
        return amount;
    }, this);

    //Shelter Section
    this.firstName = "TOTAL";
    this.shelterRent = ko.observable(0);
    this.shelterWater = ko.observable(0);
    this.shelterElectricity = ko.observable(0);
    this.shelterCheckboxTotal = ko.pureComputed(function () {
        var totalAmount = 0;
        if (this.shelterStartupBool()) {
            totalAmount += parseFloat(this.shelterStartupAmount());
        }
        if (this.shelterTwoBool()) {
            totalAmount += parseFloat(this.shelterTwoAmount());
        }
        return totalAmount;
    }, this);
    this.shelterTotal = ko.pureComputed(function () {
        return parseFloat(this.shelterRent()) + parseFloat(this.shelterWater()) + parseFloat(this.shelterElectricity()) + parseFloat(this.shelterCheckboxTotal());
    }, this);
    this.shelterStartupBool = ko.observable(false);
    this.shelterStartupAmount = ko.observable(71800);
    this.shelterTwoBool = ko.observable(false);
    this.shelterTwoAmount = ko.observable(36800);

    //Food and Gas Section
    this.foodGasNumberOfGirls = ko.observable(0);
    this.foodGasMultiplierBefore = ko.observable(100);
    this.foodGasMultiplierAfter = ko.observable(3);
    this.limboNumberOfGirls = ko.observable(0);
    this.limboMultiplier = ko.observable(100);
    this.limboNumberOfDays = ko.observable(1);
    this.foodGasInterceptedGirls = ko.pureComputed(function () {
        return parseFloat(this.foodGasMultiplierBefore()) * parseFloat(this.foodGasNumberOfGirls()) * parseFloat(this.foodGasMultiplierAfter());
    }, this);
    this.foodGasLimboGirls = ko.pureComputed(function () {
        return parseFloat(this.limboMultiplier()) * parseFloat(this.limboNumberOfGirls()) * parseFloat(this.limboNumberOfDays());
    }, this);
    this.foodTotal = ko.computed(function () {
        return parseFloat(this.foodGasInterceptedGirls()) + parseFloat(this.foodGasLimboGirls());
    }, this);

    //Communication section
    this.commChairBool = ko.observable(false);
    this.commChairAmount = ko.observable(1000);
    this.commManagerBool = ko.observable(false);
    this.commManagerAmount = ko.observable(1000);
    this.commNumberOfStaffWt = ko.observable(0);
    this.commNumberOfStaffWtMultiplier = ko.observable(100);
    this.commEachStaffWt = ko.observable(0);
    this.commEachStaffWtMultiplier = ko.observable(300);
    this.commManagerTotal = ko.computed(function () {
        var amount = 0;

        if (this.commChairBool()) {
            amount += parseFloat(this.commChairAmount());
        }
        if (this.commManagerBool()) {
            amount += parseFloat(this.commChairAmount());
        }
        return amount;
    }, this);

    this.commNumberOfStaffTotal = ko.computed(function () {
        return parseFloat(this.commNumberOfStaffWt()) * parseFloat(this.commNumberOfStaffWtMultiplier());
    }, this);

    this.commEachStaffTotal = ko.computed(function () {
        return parseFloat(this.commEachStaffWt()) * parseFloat(this.commEachStaffWtMultiplier());
    }, this);

    this.commTotal = ko.computed(function () {
        return parseFloat(this.commManagerTotal()) + parseFloat(this.commNumberOfStaffTotal()) + parseFloat(this.commEachStaffTotal());
    }, this);
}

ko.applyBindings(new budgetViewModel());
