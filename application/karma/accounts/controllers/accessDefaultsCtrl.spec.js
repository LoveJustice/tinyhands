describe('AccessDefaultsCtrl', function(){
	var controller,
		scope,
		mockPermissionSetsService,
		mockWindow,
		$q;

	var oldPermissions = {
		is_used_by_accounts: true, 
		name: "Foo",
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
		permission_address2_manage: true,
		permission_budget_manage: true,
	}
	
	var newPermissions = {
		is_new: true,
		is_used_by_accounts: true, 
		name: "Bar",
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
		permission_address2_manage: true,
		permission_budget_manage: true,
	}

	beforeEach(module('AccountsMod'));

	beforeEach(inject(function($rootScope, $controller, _$q_){
		$q = _$q_;
		
		mockPermissionSetsService = jasmine.createSpyObj('mockPermissionSetsService', ['all','get','create','update', 'destroy']);
		mockPermissionSetsService.all.and.returnValue({$promise: $q.when({results: [oldPermissions]})});

		mockWindow = {onbeforeunload: null};
        scope = $rootScope.$new();
        controller = $controller('AccessDefaultsCtrl', {
			$window: mockWindow,
			PermissionsSets: mockPermissionSetsService
		});


    }));

	it('should get all PermissionsSets', function() {
		expect(mockPermissionSetsService.all).toHaveBeenCalled();
	});
	
	it('should set permissionsSets', function() {
		scope.$apply();

		expect(controller.permissionsSets).toEqual([oldPermissions]);
	});

	it('should set onbeforeunload', function() {
		scope.$apply();

		expect(mockWindow.onbeforeunload instanceof Function).toBeTruthy();
	})
	
	describe('$window.onbeforeunload', function() {
		
		it('when a permissions set is new should return message', function() {
			controller.permissionsSets = [{is_new: false}, {is_new: true}];

			var result = mockWindow.onbeforeunload();

			expect(result).toEqual("You have unsaved changes.");
		});
		
		it('when a permissions set is not new should return undefined', function() {
			controller.permissionsSets = [{is_new: false}, {is_new: false}];
			
			var result = mockWindow.onbeforeunload();
			
			expect(result).toBeUndefined();
		})
	});
	
	describe('delete', function() {
		
		it('when permission set is used by accounts should not remove set from list', function() {
			var initialPermissionsSets = [{is_new: false, is_used_by_accounts: true}, {is_new: false, is_used_by_accounts: true}];
			var initialLength = initialPermissionsSets.length;
			controller.permissionsSets = initialPermissionsSets;
			
			controller.delete(1);
			
			expect(controller.permissionsSets.length).toEqual(initialLength);
		});
		
		it('when permission set is not used by accounts and is new should remove set from list', function() {
			var initialPermissionsSets = [{is_new: false, is_used_by_accounts: true}, {is_new: true, is_used_by_accounts: false}];
			var initialLength = initialPermissionsSets.length;
			controller.permissionsSets = initialPermissionsSets;
			
			controller.delete(1);
			
			expect(controller.permissionsSets.length).toEqual(initialLength - 1);
		});
		
		describe('when permission set is not used by accounts and is not new', function() {
			it('should destroy permission set', function() {
				var initialPermissionsSets = [{is_new: false, is_used_by_accounts: true}, {is_new: false, is_used_by_accounts: false}];
				var initialLength = initialPermissionsSets.length;
				controller.permissionsSets = initialPermissionsSets;
				mockPermissionSetsService.destroy.and.returnValue({$promise: $q.when(true)});
				
				controller.delete(1);
				scope.$apply();
				
				expect(mockPermissionSetsService.destroy).toHaveBeenCalled();
			});
			
			it('should remove permission set from list', function() {
				var initialPermissionsSets = [{is_new: false, is_used_by_accounts: true}, {is_new: false, is_used_by_accounts: false}];
				var initialLength = initialPermissionsSets.length;
				controller.permissionsSets = initialPermissionsSets;
				mockPermissionSetsService.destroy.and.returnValue({$promise: $q.when(true)});
				
				controller.delete(1);
				scope.$apply();				
				
				expect(controller.permissionsSets.length).toEqual(initialLength - 1);
			});
		});
				
	});
	
	describe('addAnother', function() {
		it('should add blank permissions set to list', function() {
			var initialPermissionsSets = [];
			var initialLength = initialPermissionsSets.length;
			controller.permissionsSets = initialPermissionsSets;
			
			controller.addAnother();
			
			expect(controller.permissionsSets.length).toEqual(initialLength + 1);
			permissionSet = controller.permissionsSets[0];
			expect(permissionSet.is_new).toEqual(true);
			expect(permissionSet.is_used_by_accounts).toEqual(false);
			expect(permissionSet.name).toEqual("");
			expect(permissionSet.permission_accounts_manage).toEqual(false);
			expect(permissionSet.permission_border_stations_add).toEqual(false);
			expect(permissionSet.permission_border_stations_delete).toEqual(false);
			expect(permissionSet.permission_border_stations_edit).toEqual(false);
			expect(permissionSet.permission_border_stations_view).toEqual(false);
			expect(permissionSet.permission_budget_manage).toEqual(false);
			expect(permissionSet.permission_irf_add).toEqual(false);
			expect(permissionSet.permission_irf_delete).toEqual(false);
			expect(permissionSet.permission_irf_edit).toEqual(false);
			expect(permissionSet.permission_irf_view).toEqual(false);
			expect(permissionSet.permission_receive_email).toEqual(false);
			expect(permissionSet.permission_address2_manage).toEqual(false);		
			expect(permissionSet.permission_vif_add).toEqual(false);		
			expect(permissionSet.permission_vif_delete).toEqual(false);		
			expect(permissionSet.permission_vif_edit).toEqual(false);		
			expect(permissionSet.permission_vif_view).toEqual(false);		
		});
	});
	
	describe('saveAll', function() {
		it('should save all permissions sets', function() {
			controller.permissionsSets = [{is_new: false, is_used_by_accounts: true}, {is_new: false, is_used_by_accounts: false}];
			mockPermissionSetsService.update.and.returnValue({$promise: $q.reject('Error')});
			
			controller.saveAll();
			
			expect(mockPermissionSetsService.update.calls.count()).toEqual(controller.permissionsSets.length);
		});
		
		describe('when permissions set is new', function() {
			it('should create permissions set', function() {
				controller.permissionsSets = [newPermissions];
				mockPermissionSetsService.create.and.returnValue({$promise: $q.when(oldPermissions)});
				
				controller.saveAll();
				scope.$apply();
				
				expect(mockPermissionSetsService.create).toHaveBeenCalledWith(newPermissions);				
			});
			
			it('should replace permissions set in list with returned set', function() {
				controller.permissionsSets = [newPermissions];
				mockPermissionSetsService.create.and.returnValue({$promise: $q.when(oldPermissions)});
				
				controller.saveAll();
				scope.$apply();
				
				expect(controller.permissionsSets[0]).toEqual(oldPermissions);				
			});
		});
		
		describe('when permissions set is not new', function() {
			it('should update permissions set', function() {
				controller.permissionsSets = [oldPermissions];
				mockPermissionSetsService.update.and.returnValue({$promise: $q.when(newPermissions)});
				
				controller.saveAll();
				scope.$apply();
				
				expect(mockPermissionSetsService.update).toHaveBeenCalledWith(oldPermissions);				
			});
			
			it('should replace permissions set in list with returned set', function() {
				controller.permissionsSets = [oldPermissions];
				mockPermissionSetsService.update.and.returnValue({$promise: $q.when(newPermissions)});
				
				controller.saveAll();
				scope.$apply();
				
				expect(controller.permissionsSets[0]).toEqual(newPermissions);				
			});
		});
		
		describe('when error creating permissions set', function() {
			it('should set controller.nameError to true', function() {
				var permissionsSet = {is_new: true, is_used_by_accounts: false};
				controller.permissionsSets = [permissionsSet];
				mockPermissionSetsService.create.and.returnValue({$promise: $q.reject('Error')});
				
				controller.saveAll();
				scope.$apply();
				
				expect(controller.nameError).toEqual(true);				
			});
			
			it('should set permissionsSet.nameError to true', function() {
				var permissionsSet = {is_new: true, is_used_by_accounts: false};
				controller.permissionsSets = [permissionsSet];
				mockPermissionSetsService.create.and.returnValue({$promise: $q.reject('Error')});
				
				controller.saveAll();
				scope.$apply();
				
				expect(permissionsSet.nameError).toEqual(true);				
			});
		});
		
		describe('when error updating permissions set', function() {
			it('should set controller.nameError to true', function() {
				var permissionsSet = {is_new: false, is_used_by_accounts: false};
				controller.permissionsSets = [permissionsSet];
				mockPermissionSetsService.update.and.returnValue({$promise: $q.reject('Error')});
				
				controller.saveAll();
				scope.$apply();
				
				expect(controller.nameError).toEqual(true);				
			});
			
			it('should set permissionsSet.nameError to true', function() {
				var permissionsSet = {is_new: false, is_used_by_accounts: false};
				controller.permissionsSets = [permissionsSet];
				mockPermissionSetsService.update.and.returnValue({$promise: $q.reject('Error')});
				
				controller.saveAll();
				scope.$apply();
				
				expect(permissionsSet.nameError).toEqual(true);				
			});
		});
	});
});
