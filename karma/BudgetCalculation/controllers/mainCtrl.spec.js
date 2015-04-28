describe('MainCtrl', function(){
    var scope;//we'll use this scope in our tests

    //mock Application to allow us to inject our own dependencies
    beforeEach(module('BudgetCalculation'));

    beforeEach(inject(function($rootScope, $controller, _$httpBackend_){
        //create an empty scope that we can use in our tests if we need it.
        scope = $rootScope.$new();
        $httpBackend = _$httpBackend_;
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
});