var constants = require('../testConstants.json');
var loginPage = require('./loginPage.js');
var permissionsPage = require('./permissionsPage.js');
var vifPage = require('./vifPage.js');

describe('Accounts Page', function() {
    
    beforeEach(function() {
        return browser.ignoreSynchronization = true;
    });

    it('should have a title', function() {
        loginPage.loginAsAdmin();
        permissionsPage.navigateToAccounts();
        expect(browser.getTitle()).toContain('All Accounts');
    });

    it('should have an access control link', function(){
        permissionsPage.navigateToAccessControl();
        expect(browser.driver.getCurrentUrl()).toContain('/accounts/access-control/');
    });

    describe('handles permissions of vif', function() {

        it('unchecks vif view permission', function(){
            permissionsPage.navigateToAccountPage();
            permissionsPage.resetPermissions();
            permissionsPage.checkPermission("id_permission_vif_view");
            this.permissions = element(by.id("id_permission_vif_view"));
            expect(this.permissions.element(by.xpath('..')).getAttribute('class')).toBe('btn btn-danger');
            permissionsPage.savePermissions();
            //permissionsPage.navigateToAccountPage();
            //permissionsPage.checkPermission("id_permission_vif_view");
            //permissionsPage.savePermissions();

            //I need to view the vif list page, I'll wait for code from Jordan and Matt to do these kinds of tests.
            //TODO test for inability to view VIFS
            permissionsPage.navigateToVifPage();
            //expect(element(by.className("table table-striped table-condensed")).isPresent()).toBe(false);
        });

        it('unchecks vif edit permission', function(){
            permissionsPage.navigateToAccountPage();
            permissionsPage.resetPermissions();
            permissionsPage.checkPermission("id_permission_vif_edit");
            this.permissions = element(by.id("id_permission_vif_edit"));
            expect(this.permissions.element(by.xpath('..')).getAttribute('class')).toBe('btn btn-danger');
            permissionsPage.savePermissions();

            permissionsPage.navigateToVifPage();
            expect(element(by.linkText("Edit")).isPresent()).toBe(false);


        });

    });

    it('allows creation of vif', function() {
        permissionsPage.navigateToVifPage();
        vifPage.createVif();
        //expect(browser.getTitle()).toContain("Create VIF");
        vifPage.filloutVif();
        //permissionsPage.navigateToAccountPage();
        //permissionsPage.uncheckAllPermissions();
    });


});
