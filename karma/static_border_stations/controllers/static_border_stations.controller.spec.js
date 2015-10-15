describe('BorderStationsCtrl', function(){
    var vm, scope, httpBackend;//we'll use this scope in our tests

    //mock Application to allow us to inject our own dependencies
    beforeEach(module('BorderStationsMod'));
    //mock the controller for the same reason and include $rootScope and $controller
    beforeEach(inject(function($rootScope, $controller, $httpBackend){
        httpBackend = $httpBackend;

        //create an empty scope
        scope = $rootScope.$new();
        //declare the controller and inject our empty scope
        vm = $controller('BorderStationsCtrl', {$scope: scope});
    }));
   // tests start here
	 
	 
	 
});