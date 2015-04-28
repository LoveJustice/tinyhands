
describe('TallyCtrl', function(){
    var vm, scope, $httpBackend;//we'll use this scope in our tests

    //mock Application to allow us to inject our own dependencies
    beforeEach(module('PortalMod'));
    //mock the controller for the same reason and include $rootScope and $controller
    beforeEach(inject(function($rootScope, $controller, _$httpBackend_){
        $httpBackend = _$httpBackend_;
        // Hook http requests here

        //create an empty scope
        scope = $rootScope.$new();
        //declare the controller and inject our empty scope
        vm = $controller('TallyCtrl', {$scope: scope});
    }));
   // tests start here

    it('should return css style if day changed and not seen', function() {
        // REGION: Data Setup
        var day = {};
        day.change = true;
        day.seen = false;
        // ENDREGION: Data Setup
        var style = vm.changeColor(day);
        expect(style).toBeDefined();
    });

    it('should return undefined if day not changed and seen', function() {
        // REGION: Data Setup
        var day = {};
        day.change = false;
        day.seen = true;
        // ENDREGION: Data Setup
        var style = vm.changeColor(day);
        expect(style).toBeUndefined();
    });

    it('should days that have not been seen or changed', function() {
        // Should test getTallyData on first call
    });

    it('should days that have been seen and changed', function() {
        // Should test getTallyData on proceeding calls
    });

    it('should change day to seen', function() {
        // REGION: Data Setup
        var day = {};
        day.seen = false;
        // ENDREGION: Data Setup
        vm.onMouseLeave(day);
        expect(day.seen).toBeTruthy();
    });

    it('should sum up interceptions', function() {
        // REGION: Data Setup
        var day = {};
        day.interceptions = {'ABC':1,'BAC':2,'CAB':3};
        // ENDREGION: Data Setup
        var sum = vm.sumNumIntercepts(day);
        expect(sum).toBe(6);
    });

    it('should send boolean to toggle vdc layer on map', function(){
        // Test that emit is called with boolean
    });
});
