describe('EditAccountCtrl', function(){
	var controller,
		scope,
		mockAccountsService,
		mockPermissionSetsService,
		mockWindow,
		accountSuccessResponse,
		accountFailureResponse,
		permissionsSetsSuccessResponse,
		permissionsSetsFailureResponse,
		$q;

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

	var blankAccount = {
		email: '',
		first_name: '',
		last_name: '',
		user_designation: '',
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

	var newAccount = {
		email: 'foo@test.org',
		first_name: 'foo',
		last_name: 'bar',
		user_designation: 'Super User',
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
	};

	beforeEach(module('AccountsMod'));

	beforeEach(inject(function($rootScope, $controller, _$q_){
		mockAccountsService = jasmine.createSpyObj('mockAccountsService', ['get','create','update']);
		mockAccountsService.get.and.callFake(function() {
			return blankAccount;
		})

		mockPermissionSetsService = jasmine.createSpyObj('mockPermissionSetsService', ['all','get']);

		mockWindow = {
			location: {
				href: '/accounts/1'
			},
			account_id: 1
		};

        scope = $rootScope.$new();
        controller = $controller('EditAccountCtrl', {
			$scope: scope,
			Accounts: mockAccountsService,
			PermissionsSets: mockPermissionSetsService,
			$window: mockWindow
		});

		$q = _$q_;

    }));

	it('should get all PermissionsSets', function() {
		expect(mockPermissionSetsService.all).toHaveBeenCalled();
	});

	describe('when window.account_id set', function() {

		beforeEach(function() {
			mockWindow.account_id = 1;
			controller.start();
		});

		it('should set vm.editing to true', function() {
			expect(controller.editing).toBe(true);
		})

		it('should get account from Accounts service', function() {
			expect(mockAccountsService.get).toHaveBeenCalledWith({id: 1});
		})
	});

	describe('when window.account_id set', function() {

		beforeEach(function() {
			mockWindow.account_id = 1;
			controller.start();
		});

		it('should set vm.editing to true', function() {
			expect(controller.editing).toBe(true);
		})

		it('should get account from Accounts service', function() {
			expect(mockAccountsService.get).toHaveBeenCalledWith({id: 1});
		})
	});

	describe('checkFields', function() {

		it('when vm.account.email is null should set vm.emailError', function () {
			controller.account = blankAccount;

			controller.checkFields();

			expect(controller.emailError).toEqual('An email is required.');
		});

		it('when vm.account.email is null should return false', function () {
			controller.account = blankAccount;

			var result = controller.checkFields();

			expect(result).toEqual(false);
		});

		it('when vm.account.email is null vm.emailError should not be set', function () {
			controller.account = newAccount;

			var result = controller.checkFields();

			expect(controller.emailError).toEqual('');
		});

		it('when vm.account.userDesignation is null should set vm.emailError', function () {
			controller.account = blankAccount;

			controller.checkFields();

			expect(controller.userDesignationError).toEqual('A user designation is required.');
		});

		it('when vm.account.userDesignation is null should return false', function () {
			controller.account = blankAccount;

			var result = controller.checkFields();

			expect(result).toEqual(false);
		});

		it('when vm.account.userDesignation is not null vm.userDesignationError should not be set', function () {
			controller.account = newAccount;

			controller.checkFields();

			expect(controller.userDesignationError).toEqual('');
		});

		it('when vm.account.email and vm.account.userDesignation are not null should return true', function () {
			controller.account = newAccount;

			var result = controller.checkFields();

			expect(result).toEqual(true);
		});
	})

	describe('update', function() {

		it('when checkFields returns false should not create or update account', function() {
			spyOn(controller, 'checkFields').and.returnValue(false);
			mockAccountsService.update.and.returnValue({$promise: $q.when(blankAccount)});

			controller.update();

			expect(mockAccountsService.update.calls.any()).toEqual(false);
		})

		it('when vm.editing is true should call Accounts.update with vm.account', function () {
			controller.editing = true;
			controller.account = newAccount;
			mockAccountsService.update.and.returnValue({$promise: $q.when(blankAccount)});

			controller.update();

			expect(mockAccountsService.update).toHaveBeenCalledWith(controller.account);
		});

		it('when vm.editing is false should call Accounts.create with vm.account', function () {
			controller.editing = false;
			controller.account = newAccount;
			mockAccountsService.create.and.returnValue({$promise: $q.when(blankAccount)});

			controller.update();

			expect(mockAccountsService.create).toHaveBeenCalledWith(controller.account);
		});

		it('should redirect to accounts page', function () {
			controller.editing = true;
			controller.account = newAccount;

			mockAccountsService.update.and.returnValue({$promise: $q.when(blankAccount)});

			controller.update();
			scope.$apply();

			expect(mockWindow.location.href).toBe('/accounts')
		});

		it('when Accounts.update returns email error should set vm.emailError', function () {
			controller.editing = true;
			controller.account = newAccount;
			var errorMessage = 'Enter a valid email';
			var promise = $q.defer();

			mockAccountsService.update.and.returnValue({$promise: promise.promise});

			controller.update();
			promise.reject({data: {email: [errorMessage] }});
			scope.$apply();

			expect(controller.emailError).toEqual(errorMessage);
		});
	})

	describe('getTitle', function() {
		describe('when controller.editing is true', function() {
			it('should return correct Title with correct name ', function() {
				var firstName = 'Bob';
				var lastName = 'Smith';

				controller.editing = true;
				controller.account = {first_name: firstName, last_name: lastName };

				var title = controller.getTitle();

				expect(title).toBe('Edit ' + firstName + ' ' + lastName + "'s Account");
			});
		});

		describe('when controller.editing is false', function() {
			it('should return correct title', function() {
				controller.editing = false;

				var title = controller.getTitle();

				expect(title).toBe('Create Account');
			});
		});
	});

	describe('onUserDesignationChanged', function() {
		it('should get PermissionsSet by id', function() {
			var id = 1;
			mockPermissionSetsService.get.and.returnValue({$promise: $q.when(fakePermissions)});

			controller.onUserDesignationChanged(id);
			scope.$apply();

			expect(mockPermissionSetsService.get).toHaveBeenCalledWith({id: id});
		});

		it('should set account permissions', function() {
			var id = 1;
			mockPermissionSetsService.get.and.returnValue({$promise: $q.when(fakePermissions)});

			controller.onUserDesignationChanged(id);
			scope.$apply();

			expect(controller.account.permission_irf_view).toBe(fakePermissions.permission_irf_view);
			expect(controller.account.permission_irf_add).toBe(fakePermissions.permission_irf_add);
			expect(controller.account.permission_irf_edit).toBe(fakePermissions.permission_irf_edit);
			expect(controller.account.permission_irf_delete).toBe(fakePermissions.permission_irf_delete);
			expect(controller.account.permission_vif_view).toBe(fakePermissions.permission_vif_view);
			expect(controller.account.permission_vif_add).toBe(fakePermissions.permission_vif_add);
			expect(controller.account.permission_vif_edit).toBe(fakePermissions.permission_vif_edit);
			expect(controller.account.permission_vif_delete).toBe(fakePermissions.permission_vif_delete);
			expect(controller.account.permission_border_stations_view).toBe(fakePermissions.permission_border_stations_view);
			expect(controller.account.permission_border_stations_add).toBe(fakePermissions.permission_border_stations_add);
			expect(controller.account.permission_border_stations_edit).toBe(fakePermissions.permission_border_stations_edit);
			expect(controller.account.permission_border_stations_delete).toBe(fakePermissions.permission_border_stations_delete);
			expect(controller.account.permission_accounts_manage).toBe(fakePermissions.permission_accounts_manage);
			expect(controller.account.permission_receive_email).toBe(fakePermissions.permission_receive_email);
			expect(controller.account.permission_vdc_manage).toBe(fakePermissions.permission_vdc_manage);
			expect(controller.account.permission_budget_manage).toBe(fakePermissions.permission_budget_manage);
		});
	});

	describe('getButtonText', function() {
		describe('when has_permission is true', function() {
			it('should return "Yes"', function() {
				var has_permission = true;
				var text = controller.getButtonText(has_permission);

				expect(text).toBe('Yes');
			});
		});

		describe('when has_permission is false', function() {
			it('should return "No"', function() {
				var has_permission = false;
				var text = controller.getButtonText(has_permission);

				expect(text).toBe('No');
			});
		});
	});

	describe('getUpdateButtonText', function() {
		describe('when controller.editing is true', function() {
			it('should return "Update"', function() {
				controller.editing = true;
				var text = controller.getUpdateButtonText();

				expect(text).toBe('Update');
			});
		});

		describe('when controller.editing is false', function() {
			it('should return "Create"', function() {
				controller.editing = false;
				var text = controller.getUpdateButtonText();

				expect(text).toBe('Create');
			});
		});
	});


});
