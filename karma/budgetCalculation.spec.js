describe('MainCtrl', function(){
    var scope, httpBackend, controller;//we'll use this scope in our tests

    //mock Application to allow us to inject our own dependencies
    beforeEach(module('BudgetCalculation'));

    beforeEach(inject(function($rootScope, $controller, $httpBackend){
        //create an empty scope that we can use in our tests if we need it.
        scope = $rootScope.$new();
        httpBackend = $httpBackend;
        //declare the controller and inject our empty scope. 
        //Remember vm=this so you can access stuff on vm by saying controller.variable or controller.function

        controller = $controller('MainCtrl', {$scope: scope});
    }));

    // tests start here
    it('should have a MainCtrl', function(){
        expect(controller).toBeDefined();
        //console.log(controller); //Good way to make sure stuff is actually there, or what is happening in reality
    });

    it('should have a form variable', function(){
       expect(controller.form).toBeDefined();
    });

    it('retrieves the form correctly', function() {
        httpBackend.expectGET('/budget/api/budget_calculations/1/').respond(200, {
            shelter_water: 0,
            shelter_electricity: 3
        });
        controller.retrieveForm(1);
        httpBackend.flush();
        expect(controller.form.shelter_water).toBe(0);
        expect(controller.form.shelter_electricity).toBe(3);
    });

    it('creates the form correctly', function() {
        controller.test = true;
        httpBackend.expectPOST('/budget/api/budget_calculations/', controller.form).respond(200, {
           id: 2
        });
        controller.createForm();
        httpBackend.flush();
        expect(controller.id).toBe(2)
    });

    it('updates the form correctly', function() {
        controller.test = true;
        controller.form.id = 2;
        httpBackend.expectPUT('/budget/api/budget_calculations/2/', controller.form).respond(200, {
           id: 3
        });
        controller.updateForm();
        httpBackend.flush();
        expect(controller.id).toBe(3)

    });
});


describe('otherBudgetItemsCtrl', function(){
    var scope;//we'll use this scope in our tests

    //mock Application to allow us to inject our own dependencies
    beforeEach(module('BudgetCalculation'));

    beforeEach(inject(function($rootScope, $controller){
        //create an empty scope
        scope = $rootScope.$new();

        controller = $controller('otherBudgetItemsCtrl', {$scope: scope});
        scope.form_section = 1;
        //declare the controller and inject our empty scope
    }));

    // tests start here
    it('should have a otherBudgetItemsCtrl', function(){
        expect(controller).toBeDefined();
    });

    it('should add a new item to travelForms (index 1 of formsList)', function(){
    	expect(controller.formsList.length).toEqual(4);
    	expect(controller.formsList[0].length).toEqual(0);

    	controller.addNewItem();
    	expect(controller.formsList[0].length).toEqual(1);
    });

    it('should remomve the item in travelForms (index 1 of formsList)', function(){
    	expect(controller.formsList.length).toEqual(4);
    	controller.formsList[0].push({id: -1})
    	expect(controller.formsList[0].length).toEqual(1);

    	controller.removeItem(-1,0);
    	expect(controller.formsList[0].length).toEqual(0);
    });

    it('should total all the budgetItems correctly', function(){
    	expect(controller.formsList.length).toEqual(4);
    	controller.otherItemsTotal();
    	expect(scope.miscItemsTotalVal).toEqual(0);

    	controller.formsList[0].push({cost: 5});
    	controller.otherItemsTotal();
    	expect(scope.miscItemsTotalVal).toEqual(5);

    	controller.formsList[0].push({cost: 5});
    	controller.otherItemsTotal();
    	expect(scope.miscItemsTotalVal).toEqual(10);

    	controller.formsList[0].pop();
    	controller.otherItemsTotal();
    	expect(scope.miscItemsTotalVal).toEqual(5);
    });

});


describe('staffCtrl', function(){
    var scope;//we'll use this scope in our tests

    //mock Application to allow us to inject our own dependencies
    beforeEach(module('BudgetCalculation'));

    beforeEach(inject(function($rootScope, $controller){
        scope = $rootScope.$new();
        controller = $controller('staffCtrl', {$scope: scope});
    }));
    

    it('should have a staffCtrl', function(){
        expect(controller).toBeDefined();
    });

    it('should total salaries correctly', function(){
        expect(controller.staffTotal).toEqual(0); //The salaries should start at zero

        //Add a new salary, should increase total to 5
        controller.staffSalaryForms.push({salary: 5});
		controller.totalSalaries();
		expect(controller.staffTotal).toEqual(5);

		//Add a new salary, should increase total to 15
        controller.staffSalaryForms.push({salary: 10});
		controller.totalSalaries();
		expect(controller.staffTotal).toEqual(15);

		//Pop the last element, should decrease back down to 5
        controller.staffSalaryForms.pop();
		controller.totalSalaries();
		expect(controller.staffTotal).toEqual(5);        
    });
});
