function shelterViewModel() {
             //Shelter Section
             this.firstName = "TOTAL";
             this.shelterRent = ko.observable(0);
             this.shelterWater = ko.observable(0);
             this.shelterElectricity = ko.observable(0);
             this.shelterCheckboxTotal = ko.pureComputed(function(){
                 var totalAmount = 0;
                 if(this.shelterStartupBool()) {
                     totalAmount += parseFloat(this.shelterStartupAmount());
                 }
                 if(this.shelterTwoBool()) {
                     totalAmount += parseFloat(this.shelterTwoAmount());
                 }
                 return totalAmount;
             }, this);

             this.shelterTotal = ko.pureComputed(function(){
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
             this.foodGasInterceptedGirls = ko.pureComputed(function(){
                 return parseFloat(this.foodGasMultiplierBefore()) * parseFloat(this.foodGasNumberOfGirls()) * parseFloat(this.foodGasMultiplierAfter());
             }, this);
             this.foodGasLimboGirls = ko.pureComputed(function(){
                 return parseFloat(this.limboMultiplier()) * parseFloat(this.limboNumberOfGirls()) * parseFloat(this.limboNumberOfDays());
             }, this);
             this.foodTotal = ko.computed(function() {
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
             this.commManagerTotal = ko.computed(function() {
                 var amount = 0;

                 if(this.commChairBool()) {
                     amount += parseFloat(this.commChairAmount());
                 }
                 if(this.commManagerBool()) {
                     amount += parseFloat(this.commChairAmount());
                 }
                 return amount;
             }, this);

             this.commNumberOfStaffTotal = ko.computed(function() {
                 return parseFloat(this.commNumberOfStaffWt()) * parseFloat(this.commNumberOfStaffWtMultiplier());
             }, this);

             this.commEachStaffTotal = ko.computed(function() {
                 return parseFloat(this.commEachStaffWt()) * parseFloat(this.commEachStaffWtMultiplier());
             }, this);

             this.commTotal = ko.computed(function() {
                 return parseFloat(this.commManagerTotal()) + parseFloat(this.commNumberOfStaffTotal()) + parseFloat(this.commEachStaffTotal());
             }, this);
         }

         ko.applyBindings(new shelterViewModel());
