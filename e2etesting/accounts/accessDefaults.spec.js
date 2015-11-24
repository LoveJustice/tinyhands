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
            expect(adminRow.irfView.getText()).toEqual('Yes');
            expect(adminRow.irfAdd.getText()).toEqual('Yes');
            expect(adminRow.irfEdit.getText()).toEqual('Yes');
            expect(adminRow.irfDelete.getText()).toEqual('Yes');
            expect(adminRow.vifView.getText()).toEqual('Yes');
            expect(adminRow.vifAdd.getText()).toEqual('Yes');
            expect(adminRow.vifEdit.getText()).toEqual('Yes');
            expect(adminRow.vifDelete.getText()).toEqual('Yes');
            expect(adminRow.borderStationView.getText()).toEqual('Yes');
            expect(adminRow.borderStationAdd.getText()).toEqual('Yes');
            expect(adminRow.borderStationEdit.getText()).toEqual('Yes');
            expect(adminRow.accountsManage.getText()).toEqual('Yes');
            expect(adminRow.alertsCanReceive.getText()).toEqual('No');                
            expect(adminRow.vdcManage.getText()).toEqual('Yes');
            expect(adminRow.budgetManage.getText()).toEqual('Yes');
        });
    });
    
    it('should have clickable permissions buttons', function() {
        accessDefaultsPage.navigateToAccessDefaults();
        accessDefaultsPage.addPermissionsSetRow();
            
        var permissionRow = accessDefaultsPage.getLastPermissionsSetRow();
        accessDefaultsPage.clickRowPermissionButtons(permissionRow);
        
        expect(permissionRow.irfView.getText()).toEqual('Yes');
        expect(permissionRow.irfAdd.getText()).toEqual('Yes');
        expect(permissionRow.irfEdit.getText()).toEqual('Yes');
        expect(permissionRow.irfDelete.getText()).toEqual('Yes');
        expect(permissionRow.vifView.getText()).toEqual('Yes');
        expect(permissionRow.vifAdd.getText()).toEqual('Yes');
        expect(permissionRow.vifEdit.getText()).toEqual('Yes');
        expect(permissionRow.vifDelete.getText()).toEqual('Yes');
        expect(permissionRow.borderStationView.getText()).toEqual('Yes');
        expect(permissionRow.borderStationAdd.getText()).toEqual('Yes');
        expect(permissionRow.borderStationEdit.getText()).toEqual('Yes');
        expect(permissionRow.accountsManage.getText()).toEqual('Yes');
        expect(permissionRow.alertsCanReceive.getText()).toEqual('Yes');                
        expect(permissionRow.vdcManage.getText()).toEqual('Yes');
        expect(permissionRow.budgetManage.getText()).toEqual('Yes');
        
        permissionRow.deleteButton.click();
    });    
     
    describe('when add another button clicked', function () {
        it('should add another row of permissions with no permissions selected', function () {
            accessDefaultsPage.navigateToAccessDefaults();
            accessDefaultsPage.addPermissionsSetRow();
            
            var permissionRow = accessDefaultsPage.getLastPermissionsSetRow();
            expect(permissionRow.designation.getText()).toEqual('');
            expect(permissionRow.irfView.getText()).toEqual('No');
            expect(permissionRow.irfAdd.getText()).toEqual('No');
            expect(permissionRow.irfEdit.getText()).toEqual('No');
            expect(permissionRow.irfDelete.getText()).toEqual('No');
            expect(permissionRow.vifView.getText()).toEqual('No');
            expect(permissionRow.vifAdd.getText()).toEqual('No');
            expect(permissionRow.vifEdit.getText()).toEqual('No');
            expect(permissionRow.vifDelete.getText()).toEqual('No');
            expect(permissionRow.borderStationView.getText()).toEqual('No');
            expect(permissionRow.borderStationAdd.getText()).toEqual('No');
            expect(permissionRow.borderStationEdit.getText()).toEqual('No');
            expect(permissionRow.accountsManage.getText()).toEqual('No');
            expect(permissionRow.alertsCanReceive.getText()).toEqual('No');                
            expect(permissionRow.vdcManage.getText()).toEqual('No');
            expect(permissionRow.budgetManage.getText()).toEqual('No');
            
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
            permissionRow.irfView.click();
            accessDefaultsPage.saveAll();
            browser.sleep(2000);
            
            accessDefaultsPage.navigateToAccessDefaults();
            var lastRow = accessDefaultsPage.getLastPermissionsSetRow();
            
            expect(lastRow.designation.getAttribute('value')).toEqual(name);
            expect(permissionRow.irfView.getText()).toEqual('Yes');
            expect(permissionRow.irfAdd.getText()).toEqual('No');
            expect(permissionRow.irfEdit.getText()).toEqual('No');
            expect(permissionRow.irfDelete.getText()).toEqual('No');
            expect(permissionRow.vifView.getText()).toEqual('No');
            expect(permissionRow.vifAdd.getText()).toEqual('No');
            expect(permissionRow.vifEdit.getText()).toEqual('No');
            expect(permissionRow.vifDelete.getText()).toEqual('No');
            expect(permissionRow.borderStationView.getText()).toEqual('No');
            expect(permissionRow.borderStationAdd.getText()).toEqual('No');
            expect(permissionRow.borderStationEdit.getText()).toEqual('No');
            expect(permissionRow.accountsManage.getText()).toEqual('No');
            expect(permissionRow.alertsCanReceive.getText()).toEqual('No');                
            expect(permissionRow.vdcManage.getText()).toEqual('No');
            expect(permissionRow.budgetManage.getText()).toEqual('No');
            
            lastRow.deleteButton.click();
        }); 
    })    
});
