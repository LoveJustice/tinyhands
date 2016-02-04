describe('accountsCtrl', function(){
  var controller,
    scope,
    mockModal,
    mockAccountsService,
		mockPermissionSetsService,
    $q;

  var account = {
		first_name: 'foo',
  	last_name: 'bar',
    id: '1',
  };

  beforeEach(module("AccountsMod"));

  beforeEach(inject(function($rootScope, $controller, _$q_){
    $q = _$q_;

    mockModal = jasmine.createSpyObj('mockModal', ['open']);

    mockAccountsService = jasmine.createSpyObj('mockAccountsService', ['all','me','update','resendActivationEmail','destroy']);

    mockPermissionSetsService = jasmine.createSpyObj('mockPermissionSetsService', ['all']);

    scope = $rootScope.$new();
    controller = $controller('AccountsCtrl', {
      Accounts: mockAccountsService,
      PermissionsSets: mockPermissionSetsService,
      $modal: mockModal
    });
  }));

  describe('on start', function(){
    it('should get all accounts', function(){
      expect(mockAccountsService.all).toHaveBeenCalled();
    });

    it('should get all permission sets', function(){
      expect(mockPermissionSetsService.all).toHaveBeenCalled();
    });

    it('should get current user', function(){
      expect(mockAccountsService.me).toHaveBeenCalled();
    });

  });

  describe('when resendActivationEmail button onclick', function(){
    it('should call resendActivationEmail with the id of the user', function(){
      var id = 1;
      controller.resendActivationEmail(id);

      expect(mockAccountsService.resendActivationEmail).toHaveBeenCalledWith({id:id});
    });
  });

  describe('when delete button onclick', function(){
    var user_name = account.first_name+' '+account.last_name;

    it('should open a modal', function(){
      mockModal.open.and.returnValue({result: $q.when(true)});
      mockAccountsService.destroy.and.returnValue({$promise: $q.when(true)});
      controller.openModal(account);
      scope.$apply();

      expect(mockModal.open.calls.mostRecent().args[0].templateUrl).toEqual("modal.html");
      expect(mockModal.open.calls.mostRecent().args[0].controller).toEqual("ModalCtrl");
      expect(mockModal.open.calls.mostRecent().args[0].controllerAs).toEqual("modalCtrl");
      expect(mockModal.open.calls.mostRecent().args[0].resolve.user_name()).toEqual(user_name);
    });

    it('should delete the account after the result', function(){
      mockModal.open.and.returnValue({result: $q.when(true)});
      mockAccountsService.destroy.and.returnValue({$promise: $q.when(true)});
      controller.openModal(account);
      scope.$apply();

      expect(mockAccountsService.destroy).toHaveBeenCalledWith({id:account.id});
    });

    it('should load all accounts after an account is deleted', function(){
      mockModal.open.and.returnValue({result: $q.when(true)});
      mockAccountsService.destroy.and.returnValue({$promise: $q.when(true)});
      controller.openModal(account);
      scope.$apply();

      expect(mockAccountsService.all).toHaveBeenCalled();
    });

  });

});
