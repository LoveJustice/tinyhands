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

    it('unchecks vif view permission', function() {
        //permissionsPage.uncheckPermission("id_permission_vif_view");
        //expect(permissionsPage.permissions).toBe(false);
        //permissionsPage.navigateToVifPage();
        //vifPage.createVif();
        //expect(browser.getTitle()).toContain("Create VIF");
    });

    it('allows creation of vif', function() {
        permissionsPage.navigateToVifPage();
        vifPage.createVif();
        expect(browser.getTitle()).toContain("Create VIF");
        vifPage.filloutVif();
        //expect(element(by.className("vif-number"))).toExist();
    });


});
