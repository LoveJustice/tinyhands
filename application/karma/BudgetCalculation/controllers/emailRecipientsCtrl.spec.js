describe('emailRecipientsCtrl', function(){
    var scope, controller;//we'll use this scope in our tests

    //mock Application to allow us to inject our own dependencies
    beforeEach(module('BudgetCalculation'));

    beforeEach(inject(function($rootScope, $controller){
        scope = $rootScope.$new();
        controller = $controller('emailRecipientsCtrl', {$scope: scope});
    }));

    it('should have a emailRecipientsCtrl', function(){
        expect(controller).toBeDefined();
    });
});
