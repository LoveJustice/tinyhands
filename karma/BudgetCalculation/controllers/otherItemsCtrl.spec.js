describe('otherBudgetItemsCtrl', function(){
    var scope, controller;//we'll use this scope in our tests

    //mock Application to allow us to inject our own dependencies
    beforeEach(module('BudgetCalculation'));

    beforeEach(inject(function($rootScope, $controller, $httpBackend){
        //create an empty scope
        scope = $rootScope.$new();
        httpBackend = $httpBackend;


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

