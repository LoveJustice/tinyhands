var constants = require('../testConstants.json');
var loginPage = require('./loginPage.js');
var permissionsPage = require('./permissionsPage.js');
var vifPage = require('../dataentry/vifPage.js');
var irfPage = require('../dataentry/irfCRUD.js');

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

    describe('handles permissions of VDCs', function(){

        it('unchecks vdc edit permission', function(){
            //uncheck permission for VDC edit
            permissionsPage.checkPermissionSetup("id_permission_vdc_manage");
            this.permissions = element(by.id("id_permission_vdc_manage"));
            expect(this.permissions.element(by.xpath("..")).getAttribute('class')).toBe('btn btn-danger');
            permissionsPage.savePermissions();

            //tests for inability to edit addresses
            permissionsPage.navigateToVdcPage();
            browser.sleep(800);
            expect(element(by.xpath('//h1')).getText()).toContain("403");

            //rechecks VDC edit permission
            permissionsPage.checkPermissionCleanup();
        });
    });

    describe('handles budget permissions', function(){
        it('unchecks budget management permission', function() {
            permissionsPage.checkPermissionSetup("id_permission_budget_manage");
            this.permissions = element(by.id("id_permission_budget_manage"));
            expect(this.permissions.element(by.xpath("..")).getAttribute('class')).toBe('btn btn-danger');
            permissionsPage.savePermissions();

            //tests for inability to edit addresses
            permissionsPage.navigateToBudgetPage();
            browser.sleep(800);
            expect(element(by.xpath('//h1')).getText()).toContain("403");

            //rechecks budget edit permission
            permissionsPage.checkPermissionCleanup();
        });
    });

    describe('handles permissions of IRF', function() {

        it('unchecks irf add permissions', function(){
            //Unchecks the add permission
            permissionsPage.checkPermissionSetup("id_permission_irf_add");
            this.permissions = element(by.id("id_permission_irf_add"));
            expect(this.permissions.element(by.xpath("..")).getAttribute('class')).toBe('btn btn-danger');
            permissionsPage.savePermissions();

            //Tests for inability to create IRFS
            permissionsPage.navigateToIrfPage();
            expect(element(by.linkText("Input A New IRF")).isPresent()).toBe(false);

            //reset permissions
            permissionsPage.checkPermissionCleanup();
        });

        it('unchecks irf view permission', function(){
            //unchecks the view permission
            permissionsPage.checkPermissionSetup("id_permission_irf_view");
            this.permissions = element(by.id("id_permission_irf_view"));
            expect(this.permissions.element(by.xpath("..")).getAttribute('class')).toBe('btn btn-danger');
            permissionsPage.savePermissions();

            //tests for inability to view IRFS
            irfPage.getToIRF();
            irfPage.fillOutIRF();
            expect(element(by.linkText("View")).isPresent()).toBe(false);

            //reset permissions
            permissionsPage.checkPermissionCleanup();
        });

        it('unchecks irf edit permission', function(){
            //unchecks the edit permission
            permissionsPage.checkPermissionSetup("id_permission_irf_edit");
            this.permissions = element(by.id("id_permission_irf_edit"));
            expect(this.permissions.element(by.xpath("..")).getAttribute('class')).toBe('btn btn-danger');
            permissionsPage.savePermissions();

            //tests for inability to edit forms
            permissionsPage.navigateToIrfPage();
            expect(element(by.linkText("Edit")).isPresent()).toBe(false);

            //resets permissions
            permissionsPage.checkPermissionCleanup();
        });

    });

    describe('handles VDC editing permission', function(){
        it('unchecks vdc edit permission', function(){
            permissionsPage.navigateToAccountPage();
            permissionsPage.resetPermissions();
            permissionsPage.checkPermission("id_permission_vdc_manage");
            this.permissions = element(by.id("id_permission_vdc_manage"));
            expect(this.permissions.element(by.xpath("..")).getAttribute('class')).toBe('btn btn-danger');
            permissionsPage.savePermissions();

            //tests for inability to edit vdc's
            browser.get(constants.webAddress + "/data-entry/geocodelocations/vdc-admin/");
            expect(element(by.xpath('//h1')).getText()).toContain("403");

            permissionsPage.navigateToAccountPage();
            permissionsPage.resetPermissions();
            permissionsPage.savePermissions();
        });


    });

    describe('handles border stations permissions', function() {
        it('unchecks borderstation view permission', function(){
            //unchecks permission
            permissionsPage.navigateToAccountPage();
            permissionsPage.resetPermissions();
            permissionsPage.checkPermission("id_permission_border_stations_view");
            this.permissions = element(by.id("id_permission_border_stations_view"));
            expect(this.permissions.element(by.xpath("..")).getAttribute('class')).toBe('btn btn-danger');
            permissionsPage.savePermissions();

            //tests for inability to view borderstations
            expect(element(by.linkText("Stations")).isPresent()).toBe(false);

            permissionsPage.navigateToAccountPage();
            permissionsPage.resetPermissions();
            permissionsPage.savePermissions();
        });

        it('unchecks borderstation edit permission', function(){
            permissionsPage.navigateToAccountPage();
            permissionsPage.resetPermissions();
            permissionsPage.checkPermission("id_permission_border_stations_edit");
            this.permissions = element(by.id("id_permission_border_stations_edit"));
            expect(this.permissions.element(by.xpath("..")).getAttribute('class')).toBe('btn btn-danger');
            permissionsPage.savePermissions();

            permissionsPage.navigateToBorderstationPage();
            expect(element(by.linkText("Update")).isPresent()).toBe(false);
            browser.get(constants.webAddress + "/static_border_stations/border-stations/update/0/");
            expect(element(by.xpath('//h1')).getText()).toContain("403");

            permissionsPage.navigateToAccountPage();
            permissionsPage.resetPermissions();
            permissionsPage.savePermissions();
        });

        it('unchecks borderstation create permission', function(){
            permissionsPage.navigateToAccountPage();
            permissionsPage.resetPermissions();
            permissionsPage.checkPermission("id_permission_border_stations_add");
            this.permissions = element(by.id("id_permission_border_stations_add"));
            expect(this.permissions.element(by.xpath("..")).getAttribute('class')).toBe('btn btn-danger');
            permissionsPage.savePermissions();

            //tests for inability to create
            browser.get(constants.webAddress + "/static_border_stations/border-stations/create/");
            expect(element(by.xpath('//h1')).getText()).toContain("403");

            permissionsPage.navigateToAccountPage();
            permissionsPage.resetPermissions();
            permissionsPage.savePermissions();
        });

    });

    describe('handles permissions of vif', function() {
        it('allows viewing of vif', function() {
            permissionsPage.navigateToVifPage();
            permissionsPage.viewVifForm();
            expect(browser.getTitle()).toContain("Edit VIF");
        });

        it('unchecks vif add permissions', function(){
            //Unchecks the add permission
            permissionsPage.navigateToAccountPage();
            permissionsPage.resetPermissions();
            permissionsPage.checkPermission("id_permission_vif_add");
            this.permissions = element(by.id("id_permission_vif_add"));
            expect(this.permissions.element(by.xpath('..')).getAttribute('class')).toBe('btn btn-danger');
            permissionsPage.savePermissions();

            //Tests for inability to create VIFS
            permissionsPage.navigateToVifPage();
            vifPage.createVif();
            expect(element(by.xpath('//h1')).getText()).toContain("403");

            //reset permissions
            permissionsPage.navigateToAccountPage();
            permissionsPage.resetPermissions();
            permissionsPage.savePermissions();
        });

        it('unchecks vif view permission', function(){
            //unchecks the view permission
            permissionsPage.navigateToAccountPage();
            permissionsPage.resetPermissions();
            permissionsPage.checkPermission("id_permission_vif_view");
            this.permissions = element(by.id("id_permission_vif_view"));
            expect(this.permissions.element(by.xpath('..')).getAttribute('class')).toBe('btn btn-danger');
            permissionsPage.savePermissions();

            //tests for inability to view VIFS
            permissionsPage.navigateToVifPage();
            expect(element(by.linkText("View")).isPresent()).toBe(false);

            //reset permissions
            permissionsPage.navigateToAccountPage();
            permissionsPage.resetPermissions();
            permissionsPage.savePermissions();
        });

        it('unchecks vif edit permission', function(){
            //unchecks the edit permission
            permissionsPage.navigateToAccountPage();
            permissionsPage.resetPermissions();
            permissionsPage.checkPermission("id_permission_vif_edit");
            this.permissions = element(by.id("id_permission_vif_edit"));
            expect(this.permissions.element(by.xpath('..')).getAttribute('class')).toBe('btn btn-danger');
            permissionsPage.savePermissions();

            //tests for inability to edit forms
            permissionsPage.navigateToVifPage();
            expect(element(by.linkText("Edit")).isPresent()).toBe(false);

            //resets permissions
            permissionsPage.navigateToAccountPage();
            permissionsPage.resetPermissions();
            permissionsPage.savePermissions();
        });

    });

    describe('handles accounts permission', function(){
        it('unchecks the account management permission', function(){

            //uncheck the permission
            permissionsPage.navigateToAccountPage();
            permissionsPage.checkPermission("id_permission_accounts_manage");
            browser.sleep(500);
            this.permissions = element(by.id("id_permission_accounts_manage"));
            expect(this.permissions.element(by.xpath("..")).getAttribute('class')).toBe('btn btn-danger');
            permissionsPage.savePermissions();
            browser.sleep(500);

            //test for inability to edit accounts
            expect(element(by.xpath('//h1')).getText()).toContain("403");

        });
    });

});
