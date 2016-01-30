describe('accessCtrl', function(){
  var controller,
    scope,
    mockModal,
    mockAccountsService,
		mockPermissionSetsService,
    $q;
    
    var newAccount = {
		email: 'foo@test.org',
		first_name: 'foo',
		last_name: 'bar',
		user_designation: 1,
		permission_irf_view: false,
		permission_irf_add: false,
		permission_irf_edit: false,
		permission_irf_delete: false,
		permission_vif_view: false,
		permission_vif_add: false,
		permission_vif_edit: false,
		permission_vif_delete: false,
		permission_border_stations_view: false,
		permission_border_stations_add: false,                
		permission_border_stations_edit: false,                
		permission_border_stations_delete: false,                
		permission_accounts_manage: false,
		permission_receive_email: false,
		permission_vdc_manage: false,
		permission_budget_manage: false,
	};
    
    var fakePermissions = {
		permission_irf_view: true,
		permission_irf_add: true,
		permission_irf_edit: true,
		permission_irf_delete: true,
		permission_vif_view: true,
		permission_vif_add: true,
		permission_vif_edit: true,
		permission_vif_delete: true,
		permission_border_stations_view: true,
		permission_border_stations_add: true,                
		permission_border_stations_edit: true,                
		permission_border_stations_delete: true,                
		permission_accounts_manage: true,
		permission_receive_email: true,
		permission_vdc_manage: true,
		permission_budget_manage: true,
	}
    

  beforeEach(module("AccountsMod"));

  beforeEach(inject(function($rootScope, $controller, _$q_){
    mockAccountsService = jasmine.createSpyObj('mockAccountsService', ['all','me','update','resendActivationEmail','destroy']);

    mockPermissionSetsService = jasmine.createSpyObj('mockPermissionSetsService', ['all', 'get']);

    scope = $rootScope.$new();
    controller = $controller('AccessCtrl', {
      Accounts: mockAccountsService,
      PermissionsSets: mockPermissionSetsService
    });
    
    $q=_$q_;
    
  }));

  describe('on start', function(){
    it('should get all accounts', function(){
      expect(mockAccountsService.all).toHaveBeenCalled();
    });

    it('should get all permission sets', function(){
      expect(mockPermissionSetsService.all).toHaveBeenCalled();
    });

  });

  describe('changeUserRole', function(){
  	it('should get proper permission set', function(){
      mockPermissionSetsService.get.and.returnValue({$promise: $q.when(fakePermissions)});
      controller.changeUserRole(newAccount);
      scope.$apply(); //applies the $q.when function's changes.
      expect(mockPermissionSetsService.get).toHaveBeenCalledWith({id: newAccount.user_designation});
	  });
  
    it('when PermissionSet received, should change each permission', function(){
      mockPermissionSetsService.get.and.returnValue({$promise: $q.when(fakePermissions)});
      controller.changeUserRole(newAccount);
      scope.$apply(); //applies the $q.when function's changes.
	  
      expect(newAccount.permission_irf_add).toEqual(fakePermissions.permission_irf_add);
      expect(newAccount.permission_irf_delete).toEqual(fakePermissions.permission_irf_delete);
      expect(newAccount.permission_irf_edit).toEqual(fakePermissions.permission_irf_edit);
      expect(newAccount.permission_irf_view).toEqual(fakePermissions.permission_irf_view);
      
      expect(newAccount.permission_vif_add).toEqual(fakePermissions.permission_vif_add);
      expect(newAccount.permission_vif_delete).toEqual(fakePermissions.permission_vif_delete);
      expect(newAccount.permission_vif_edit).toEqual(fakePermissions.permission_vif_edit);
      expect(newAccount.permission_vif_view).toEqual(fakePermissions.permission_vif_view);
      
	    expect(newAccount.permission_border_stations_add).toEqual(fakePermissions.permission_border_stations_add); 
	    expect(newAccount.permission_border_stations_delete).toEqual(fakePermissions.permission_border_stations_delete);
	    expect(newAccount.permission_border_stations_edit).toEqual(fakePermissions.permission_border_stations_edit);
	    expect(newAccount.permission_border_stations_view).toEqual(fakePermissions.permission_border_stations_view);
	  
	    expect(newAccount.permission_accounts_manage).toEqual(fakePermissions.permission_accounts_manage);
	    expect(newAccount.permission_receive_email).toEqual(fakePermissions.permission_receive_email);
	    expect(newAccount.permission_vdc_manage).toEqual(fakePermissions.permission_vdc_manage);
	    expect(newAccount.permission_budget_manage).toEqual(fakePermissions.permission_budget_manage);
     });
  });
  
  describe('update', function(){
    it('should call the update function with the account', function(){
	    //mockPermissionSetsService.get.and.returnValue({$promise: $q.when(fakePermissions)});
      controller.accounts={results: [newAccount]};
      controller.update();
	    expect(mockAccountsService.update).toHaveBeenCalledWith(newAccount);
   });
  });
}); 
