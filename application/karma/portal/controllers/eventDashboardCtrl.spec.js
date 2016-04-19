describe('EventDashboard Ctrl', function() {
    var scope, mockEventService, mockModal, controller;
    beforeEach(module('PortalMod'));

    beforeEach(inject(function($rootScope, $controller){
        scope = $rootScope.$new();
        mockEventService = jasmine.createSpyObj('mockEvent', ['dashboard']);
        mockModal = jasmine.createSpyObj('mockModal', ['open']);
        controller = $controller('EventDashboardCtrl', {Events: mockEventService, $modal: mockModal});
    }));

    describe('on controller created', function() {
        it('should get dashboard events', function() {
           expect(mockEventService.dashboard).toHaveBeenCalled();
        });
    })

    describe('showEvent', function() {
       it('should open Event Modal', function() {
            var mockEvent = {title: 'foo'};

            controller.showEvent(mockEvent);
            scope.$apply();

            expect(mockModal.open).toHaveBeenCalled();
            var modalArgs = mockModal.open.calls.mostRecent().args[0];
            expect(modalArgs.templateUrl).toEqual('modal.html');
            expect(modalArgs.controller).toEqual('EventModalCtrl');
            expect(modalArgs.controllerAs).toEqual('modalCtrl');
            expect(modalArgs.bindToController).toEqual(true);
            expect(modalArgs.resolve.event()).toEqual(mockEvent);
        });

    });
});