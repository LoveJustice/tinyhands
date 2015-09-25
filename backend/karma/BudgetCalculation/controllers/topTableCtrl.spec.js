describe('topTableCtrl', function(){
    var scope;//we'll use this scope in our tests

    //mock Application to allow us to inject our own dependencies
    beforeEach(module('BudgetCalculation'));

    beforeEach(inject(function($rootScope, $controller){
        scope = $rootScope.$new();
        controller = $controller('topTableCtrl', {$scope: scope});
    }));

    it('should have a topTableCtrl', function(){
        expect(controller).toBeDefined();
    });
});
