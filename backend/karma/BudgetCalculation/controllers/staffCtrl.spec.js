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
