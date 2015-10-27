describe('EditAccountCtrl', function(){
	var controller, 
		scope, 
		httpBackend, 
		mockAccountsService,
		mockPermissionSetsService,
		mockWindow,
		accountSuccessResponse, 
		accountFailureResponse,
		permissionsSetsSuccessResponse,
		permissionsSetsFailureResponse;
	
	beforeEach(module('AccountsMod'));
	
	beforeEach(inject(function($rootScope, $controller, $httpBackend){
        httpBackend = $httpBackend;
		
		mockAccountsService = jasmine.createSpyObj('mockAccountsService', ['get']);
		
		mockPermissionSetsService = jasmine.createSpyObj('mockPermissionSetsService', ['all']);
		
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
	/*
	describe('update', function() {
		
		it('when vm.editing is true should call Accounts.update with vm.account', function () {
			
		});
	})*/
	
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