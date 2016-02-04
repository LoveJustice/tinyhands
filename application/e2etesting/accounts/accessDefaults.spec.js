var loginPage = require('./loginPage');
var accessDefaultsPage = require('./accessDefaults');

describe('Access Defaults', function () {

    beforeEach(function() {
        browser.ignoreSynchronization = true;
        loginPage.loginAsAdmin();
        browser.ignoreSynchronization = false;
    });
    
    it('should have permissions sets loaded', function() {
        accessDefaultsPage.navigateToAccessDefaults();
        accessDefaultsPage.getSuperAdministratorRow().then(function(adminRow) {
            for(permission in adminRow.permissions) {
                if (adminRow.permissions.hasOwnProperty(permission)) {
                    if(permission == 'alertsCanReceive') {
                        expect(adminRow.permissions[permission].getText()).toEqual('No');
                    }else {
                        expect(adminRow.permissions[permission].getText()).toEqual('Yes');
                    }
                }
            }
        });
    });
    
    it('should have clickable permissions buttons', function() {
        accessDefaultsPage.navigateToAccessDefaults();
        accessDefaultsPage.addPermissionsSetRow();
            
        var permissionRow = accessDefaultsPage.getLastPermissionsSetRow();
        accessDefaultsPage.clickRowPermissionButtons(permissionRow);
        
        for(permission in permissionRow.permissions) {
            if (permissionRow.permissions.hasOwnProperty(permission)) {
                expect(permissionRow.permissions[permission].getText()).toEqual('Yes');
            }
        }
        
        permissionRow.deleteButton.click();
    });    
     
    describe('when add another button clicked', function () {
        it('should add another row of permissions with no permissions selected', function () {
            accessDefaultsPage.navigateToAccessDefaults();
            accessDefaultsPage.addPermissionsSetRow();
            
            var permissionRow = accessDefaultsPage.getLastPermissionsSetRow();
            expect(permissionRow.designation.getText()).toEqual('');
            for(permission in permissionRow.permissions) {
                if (permissionRow.permissions.hasOwnProperty(permission)) {
                    expect(permissionRow.permissions[permission].getText()).toEqual('No');
                }
            }
            
            permissionRow.deleteButton.click();        
        });
    });
    
    describe('when permissions set is used', function() {
        it('should have disabled delete button', function() {
            accessDefaultsPage.navigateToAccessDefaults();
            accessDefaultsPage.getSuperAdministratorRow().then(function(adminRow) {
                expect(adminRow.deleteButton.isEnabled()).toBeFalsy();
            });
        });
        
        describe('on hover', function() {
            it('should show tooltip', function() {
                accessDefaultsPage.navigateToAccessDefaults();
                accessDefaultsPage.getSuperAdministratorRow().then(function(adminRow) {
                    browser.actions().mouseMove(adminRow.deleteButton).perform();
                    var tooltip = element(by.css(".tooltip"));
                    expect(tooltip.isDisplayed()).toBeTruthy();
                });
            })
        });
    });
    
    describe('when save all clicked', function() {
        it('should save changes', function() {
            accessDefaultsPage.navigateToAccessDefaults();
            accessDefaultsPage.addPermissionsSetRow();
            
            var name = "Foo Set";
            var permissionRow = accessDefaultsPage.getLastPermissionsSetRow();
            permissionRow.designation.sendKeys(name);
            permissionRow.permissions.irfView.click();
            accessDefaultsPage.saveAll();
            browser.sleep(2000); //wait for all REST requests to be resolved.
            
            accessDefaultsPage.navigateToAccessDefaults();
            var lastRow = accessDefaultsPage.getLastPermissionsSetRow();
            
            expect(lastRow.designation.getAttribute('value')).toEqual(name);
            
            for(permission in lastRow.permissions) {
                if (lastRow.permissions.hasOwnProperty(permission)) {
                    if(permission == 'irfView') {
                        expect(lastRow.permissions[permission].getText()).toEqual('Yes');
                    }else {
                        expect(lastRow.permissions[permission].getText()).toEqual('No');
                    }
                }
            }
                        
            lastRow.deleteButton.click(); //remove newly created set
        }); 
    })    
});
