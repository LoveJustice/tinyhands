
describe('TallyCtrl', function(){
    var vm, scope, httpBackend;//we'll use this scope in our tests

    //mock Application to allow us to inject our own dependencies
    beforeEach(module('PortalMod'));
    //mock the controller for the same reason and include $rootScope and $controller
    beforeEach(inject(function($rootScope, $controller, $httpBackend){
        httpBackend = $httpBackend;

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
        // REGION: Data Setup
        httpBackend.whenGET('/portal/tally/days/').respond(200, {
            0:{dayOfWeek:'Sunday',interceptions: {'BSD':4}},
            1:{dayOfWeek:'Monday',interceptions: {'ABC':2}},
            2:{dayOfWeek:'Tuesday',interceptions: {'BSD':4}},
            3:{dayOfWeek:'Wednesday',interceptions: {'ABC':2}},
            4:{dayOfWeek:'Thursday',interceptions: {'BSD':4}},
            5:{dayOfWeek:'Friday',interceptions: {'ABC':2}},
            6:{dayOfWeek:'Saturday',interceptions: {'BSD':4}},
        });
        httpBackend.expectGET('/portal/tally/days/');
        // ENDREGION: Data Setup
        expect(vm.days).toEqual({});

        vm.getTallyData(true);
        httpBackend.flush();

        expect(vm.days).not.toEqual({});
        for (var i in vm.days) {
            expect(vm.days[i].change).toBeFalsy();
            expect(vm.days[i].seen).toBeFalsy();
        }
    });

    it('should days that have been seen and changed', function() {
        // REGION: Data Setup
        vm.days = {
            0:{dayOfWeek:'Sunday',interceptions: {'BSD':0}},
            1:{dayOfWeek:'Monday',interceptions: {'ABC':0}},
            2:{dayOfWeek:'Tuesday',interceptions: {'BSD':0}},
            3:{dayOfWeek:'Wednesday',interceptions: {'ABC':0}},
            4:{dayOfWeek:'Thursday',interceptions: {'BSD':0}},
            5:{dayOfWeek:'Friday',interceptions: {'ABC':0}},
            6:{dayOfWeek:'Saturday',interceptions: {'BSD':0}},
        };
        newData = {
            0:{dayOfWeek:'Sunday',interceptions: {'BSD':4}},
            1:{dayOfWeek:'Monday',interceptions: {'ABC':2}},
            2:{dayOfWeek:'Tuesday',interceptions: {'BSD':4}},
            3:{dayOfWeek:'Wednesday',interceptions: {'ABC':2}},
            4:{dayOfWeek:'Thursday',interceptions: {'BSD':4}},
            5:{dayOfWeek:'Friday',interceptions: {'ABC':2}},
            6:{dayOfWeek:'Saturday',interceptions: {'BSD':4}},
        };
        // ENDREGION: Data Setup
        expect(vm.days).not.toEqual({});

        vm.checkDifferences(newData);

        for (var i in vm.days) {
            expect(vm.days[i].change).toBeTruthy();
        }
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
});
