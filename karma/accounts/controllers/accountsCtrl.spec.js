describe('accountsCtrl', function(){
  var controller,
    scope,
    mockModal,
    mockAccountsService,
		mockPermissionSetsService;

  beforeEach(module("AccountsMod"));

  beforeEach(inject(function($rootScope, $controller){
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

    it('should update accounts', function(){
      expect(mockAccountsService.update).toHaveBeenCalled();
    });
  });



});
