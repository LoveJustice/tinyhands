describe("eventsCtrl", function() {
    var scope, controller, mockModal, $q;

    beforeEach(module('EventsMod'));

    beforeEach(inject(function($rootScope, $controller, _$q_) {
        $q = _$q_;
        scope = $rootScope.$new();
        mockModal = jasmine.createSpyObj('mockModal', ['open']);
        mockEventsService = jasmine.createSpyObj('mockEventsService', ['all']);
        controller = $controller('EventsCtrl', {$modal: mockModal});
    }));

    describe('on activate', function() {
        it('should display all the events', function() {
            expect(mockEventsService.all.toHaveBeenCalled();
        });
    });

    describe('when delete button onclick', function() {
        it('should open Modal', function() {
            var mockEvent = {title: 'foo'};

            controller.openModal(mockEvent);
            scope.$apply();

            expect(mockModal.open).toHaveBeenCalled();
            var modalArgs = mockModal.open.calls.mostRecent().args[0];
            expect(modalArgs.templateUrl).toEqual('modal.html');
            expect(modalArgs.controller).toEqual('ModalCtrl');
            expect(modalArgs.controllerAs).toEqual('modalCtrl');
            expect(modalArgs.bindToController).toEqual(true);
            expect(modalArgs.resolve.event()).toEqual(mockevent);
        });

        it('should delete the event after the result', function() {
            var mockEvent = {title: 'foo', id :1};

            mockModal.open.and.returnValue({result: $q.when(true)});
            mockEventsService .destroy.and.returnValue({$promise: $q.when(true)});
            controller.openModal(mockEvent);
            scope.$apply()

            expect(mockEventsService.destroy).toHaveBeenCalledWith({id:mockEvent.id});
        });

        it('should load all events after an event is deleted', function() {
            var mockEvent = {title: 'foo', id :1};

            mockModal.open.and.returnValue({result: $q.when(true)});
            mockEventsService .destroy.and.returnValue({$promise: $q.when(true)});
            controller.openModal(mockEvent);
            scope.$apply()

            expect(mockEventsService.all).toHaveBeenCalled();
        });
    });
});
