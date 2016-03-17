describe("modalCtrl", function() {
    var controller, mockEvent, mockModalInstance = {};

    beforeEach(module('EventsMod'));

    beforeEach(inject(function($rootScope, $controller) {
        mockEvent = {title: "Foo"};
        mockModalInstance = jasmine.createSpyObj('mockModalInstance', ['close', 'dismiss']);
        scope = $rootScope.$new();
        controller = $controller('ModalCtrl', {
            $scope: scope,
            $modalInstance: mockModalInstance,
            event: mockEvent
        });
    }));


    describe("on activate", function() {
        it('should set event to display', function() {
            expect(controller.event).toEqual(mockEvent);
        });
    });

    describe("delete", function() {
        it('should delete event', function() {
            controller.delete();

            expect(mockModalInstance.close).toHaveBeenCalledWith(true);
        });
    });

    describe("close", function() {
        it('should close modal instance', function() {
            controller.cancel();

            expect(mockModalInstance.dismiss).toHaveBeenCalledWith("cancel");
        });
    });
});
