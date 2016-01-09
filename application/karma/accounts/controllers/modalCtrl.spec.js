describe('ModalCtrl', function(){
  var controller,
    scope,
    mockModalInstance,
    user_name;

  beforeEach(module('AccountsMod'));

  beforeEach(inject(function($rootScope, $controller){
    mockModalInstance = jasmine.createSpyObj('mockModalInstance',['close','dismiss']);

    scope = $rootScope.$new();
    user_name = "Foo Bar";
    controller = $controller('ModalCtrl', {
      $scope: scope,
      $modalInstance: mockModalInstance,
      user_name: user_name
    });
  }));

  describe('on start', function(){
    it('should set user_name', function(){
      expect(scope.user_name).toEqual(user_name);
    });
  });

  describe('delete button onclick', function(){
    it("should close modalInstance and return true", function(){
      controller.delete();

      expect(mockModalInstance.close).toHaveBeenCalledWith(true);
    });
  });

  describe('cancel button onclick', function(){
    it("should dismiss modalInstance and return cancel", function(){
      controller.cancel();

      expect(mockModalInstance.dismiss).toHaveBeenCalledWith("cancel");
    });
  });

});
