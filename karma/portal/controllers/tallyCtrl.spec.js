
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

    it('should have days that have changed', function() {
        // REGION: Data Setup
        httpBackend.whenGET('/portal/tally/days/').respond(200, {
        id: 0,
        days: [
            {date:'2015-05-02T02:11:49.556',interceptions: {'BSD':4}},
            {date:'2015-05-01T02:11:49.556',interceptions: {'ABC':2}},
            {date:'2015-04-30T02:11:49.556',interceptions: {'BSD':4}},
            {date:'2015-04-29T02:11:49.556',interceptions: {'ABC':2}},
            {date:'2015-04-28T02:11:49.556',interceptions: {'BSD':4}},
            {date:'2015-04-27T02:11:49.556',interceptions: {'ABC':2}},
            {date:'2015-04-26T02:11:49.556',interceptions: {'BSD':4}},
        ]});
        httpBackend.expectGET('/portal/tally/days/');
        // ENDREGION: Data Setup
        expect(vm.days).toEqual([]);

        vm.getTallyData(true);
        httpBackend.flush();

        expect(vm.days).not.toEqual([]);
        for (var i in vm.days) {
            expect(vm.days[i].change).toBeTruthy();
            expect(vm.days[i].seen).toBeFalsy();
        }
    });

    it('should have days that have not changed', function() {
        // REGION: Data Setup
        localStorage.removeItem('tally-0');
        httpBackend.whenGET('/portal/tally/days/').respond(200, {
            id: 0,
            days: [
                {date:'2015-05-02T02:11:49.556',interceptions: {}},
                {date:'2015-05-01T02:11:49.556',interceptions: {}},
                {date:'2015-04-30T02:11:49.556',interceptions: {}},
                {date:'2015-04-29T02:11:49.556',interceptions: {}},
                {date:'2015-04-28T02:11:49.556',interceptions: {}},
                {date:'2015-04-27T02:11:49.556',interceptions: {}},
                {date:'2015-04-26T02:11:49.556',interceptions: {}},
            ]});
        httpBackend.expectGET('/portal/tally/days/');
        // ENDREGION: Data Setup
        expect(vm.days).toEqual([]);

        vm.getTallyData(true);
        httpBackend.flush();

        expect(vm.days).not.toEqual([]);
        for (var i in vm.days) {
            expect(vm.days[i].change).toBeFalsy();
            expect(vm.days[i].seen).toBeFalsy();
        }
    });

    it('should have days that have or have not changed', function() {
        // REGION: Data Setup
        vm.days = [];
        newData = [
            {date:'2015-05-02T02:11:49.556',interceptions: {'BSD':4}},
            {date:'2015-05-01T02:11:49.556',interceptions: {}},
            {date:'2015-04-30T02:11:49.556',interceptions: {}},
            {date:'2015-04-29T02:11:49.556',interceptions: {'ABC':2}},
            {date:'2015-04-28T02:11:49.556',interceptions: {}},
            {date:'2015-04-27T02:11:49.556',interceptions: {'ABC':2}},
            {date:'2015-04-26T02:11:49.556',interceptions: {'BSD':4}}
        ];
        // ENDREGION: Data Setup
        expect(vm.days).toEqual([]);

        vm.checkDifferences(newData);

        expect(vm.days).not.toEqual([]);
        for (var i in vm.days) {
            if ($.isEmptyObject(vm.days[i].interceptions)) {
                expect(vm.days[i].change).toBeFalsy();
            } else {
                expect(vm.days[i].change).toBeTruthy();
            }
            expect(vm.days[i].seen).toBeFalsy();
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

    it('should set days when local storage exists', function() {
        // REGION: Data Setup
        data = {
            id: 0,
            days: [
                {date:'2015-05-02T02:11:49.556',interceptions: {'BSD':4}},
                {date:'2015-05-01T02:11:49.556',interceptions: {'ABC':2}},
                {date:'2015-04-30T02:11:49.556',interceptions: {'BSD':4}},
                {date:'2015-04-29T02:11:49.556',interceptions: {'ABC':2}},
                {date:'2015-04-28T02:11:49.556',interceptions: {'BSD':4}},
                {date:'2015-04-27T02:11:49.556',interceptions: {'ABC':2}},
                {date:'2015-04-26T02:11:49.556',interceptions: {'BSD':4}},
            ]
        };
        localStorage.removeItem('tally'+data.id);
        // ENDREGION: Data Setup
        expect(localStorage.getItem('tally'+data.id)).toBeNull();

        localStorage.setItem('tally'+data.id, JSON.stringify(data));

        expect(localStorage.getItem('tally'+data.id)).not.toBeNull();
    });
});
