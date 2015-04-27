describe("A suite", function() {
  it("contains spec with an expectation", function() {
    expect(true).toBe(true);
  });
});

describe('MainCtrl', function(){
    var scope;//we'll use this scope in our tests

    //mock Application to allow us to inject our own dependencies
    beforeEach(module('BudgetCalculation'));
    //mock the controller for the same reason and include $rootScope and $controller

    beforeEach(inject(function($rootScope, $controller, _$httpBackend_){
        //create an empty scope
        scope = $rootScope.$new();
        $httpBackend = _$httpBackend_;
        controller = $controller('MainCtrl', {$scope: scope});
        //declare the controller and inject our empty scope
        
    }));

    // tests start here
    it('should have variable text = "Hello World!"', function(){
        console.log(controller);
        expect(scope.thingy).toBe('hello');
    });


    it('should work', function() {
        expect(controller.form).toBeDefined();
        $httpBackend.whenGET('/budget/api/budget_calculations/1/').respond([{
            id: 1,
            name: "banana"
        }]);

        //controller.retrieveForm(1);

        //$httpBackend.flush();

        //expect(controller.form.name).toBe("banana");


    });
});

