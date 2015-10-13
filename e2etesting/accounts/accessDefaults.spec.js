var loginPage = require('./loginPage');
var accessDefaultsPage = require('./accessDefaults');

describe('Access Defaults', function () {

    beforeEach(function() {
        return browser.ignoreSynchronization = true;
    });

    describe('when add another button clicked', function () {
        it('should add another row of permissions with no permissions selected', function () {
            loginPage.loginAsAdmin();
            accessDefaultsPage.navigateToAccessControl().then(function() {
                return accessDefaultsPage.addPermissionSetRow();
            }).then(function() {
                var permissionRow = accessDefaultsPage.getPermissionSetRow(3);
                expect(permissionRow.designation.getText()).toEqual('');
                expect(permissionRow.irfView.isSelected()).toBeFalsy();
                expect(permissionRow.irfAdd.isSelected()).toBeFalsy();
                expect(permissionRow.irfEdit.isSelected()).toBeFalsy();
                expect(permissionRow.irfDelete.isSelected()).toBeFalsy();
                expect(permissionRow.vifView.isSelected()).toBeFalsy();
                expect(permissionRow.vifAdd.isSelected()).toBeFalsy();
                expect(permissionRow.vifEdit.isSelected()).toBeFalsy();
                expect(permissionRow.vifDelete.isSelected()).toBeFalsy();
                expect(permissionRow.borderStationView.isSelected()).toBeFalsy();
                expect(permissionRow.borderStationAdd.isSelected()).toBeFalsy();
                expect(permissionRow.borderStationEdit.isSelected()).toBeFalsy();
                expect(permissionRow.accountsManage.isSelected()).toBeFalsy();
                expect(permissionRow.vdcManage.isSelected()).toBeFalsy();
                expect(permissionRow.budgetManage.isSelected()).toBeFalsy();
            });
        });
    });
});
