describe('MainCtrl', function(){
    var scope, httpBackend, controller, window;//we'll use this scope in our tests

    //mock Application to allow us to inject our own dependencies
    beforeEach(module('BudgetCalculation'));

    beforeEach(inject(function($rootScope, $controller, $httpBackend){
        //create an empty scope that we can use in our tests if we need it.
        scope = $rootScope.$new();
        httpBackend = $httpBackend;

        window = {location: {assign: function(){return;}}}; // inject a mocked window service so that it can't redirect
        //declare the controller and inject our empty scope.
        //Remember vm=this so you can access stuff on vm by saying controller.variable or controller.function

        controller = $controller('MainCtrl', {$scope: scope, $window: window});
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

    // FIX THIS
    it('creates the form correctly', function() {
        // controller.test = true;
        // httpBackend.expectPOST('/budget/api/budget_calculations/', controller.form).respond(200, {
        //    id: 2
        // });
        // controller.createForm();
        // httpBackend.flush();
        // expect(controller.id).toBe(2)
    });

    // FIX THIS
    it('updates the form correctly', function() {
        // controller.test = true;
        // controller.form.id = 2;
        // httpBackend.expectPUT('/budget/api/budget_calculations/2/', controller.form).respond(200, {
        //    id: 3
        // });
        // controller.updateForm();
        // httpBackend.flush();
        // expect(controller.id).toBe(3)
    });
});