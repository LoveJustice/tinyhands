var constants = require('../testConstants.json');
var loginPage = require('./loginPage.js');
var accountListPage = require('./accountList.js');

describe('Account List', function() {
  beforeEach(function() {
      browser.ignoreSynchronization = true;
      loginPage.loginAsAdmin();
      browser.ignoreSynchronization = false;
  });

  it('should populated on the first navigation to page', function() {
    accountListPage.navigateToAccountList();

    expect(browser.driver.getCurrentUrl()).toContain('/accounts/');
  });

  it("should show user's designation name and not just designation id *************************************************************", function() {
    var id = 25;
    designation = accountListPage.checkUserDesignation(id);
    expect(designation == "fail");
  });

  it('should not have delete button for current user', function() {
    accountListPage.navigateToAccountList();
    accountListPage.getAdminUserRow().then(function(adminUserRow) {
      expect(adminUserRow.element(by.buttonText('Delete')).isDisplayed()).toBe(false);
    });

  });

  it('edit button onclick should direct to the correct edit account page', function() {
    var id = 25;
    accountListPage.navigateToAccountList();
    accountListPage.navigateToEditAccountPage(id);

    expect(browser.driver.getCurrentUrl()).toContain('/accounts/update/'+id);
  });

  it('delete button onclick should show delete modal', function() {
    var id = 25;
    accountListPage.navigateToAccountList();
    accountListPage.navigateToDeleteModal(id);

    expect(element(by.className('modal-header')).isDisplayed()).toBe(true);
  });

  describe('Delete Modal', function() {
    var id = 25;
    beforeEach(function() {
      accountListPage.navigateToAccountList();
      accountListPage.navigateToDeleteModal(id);
    });

    it('cancel buttion onclick should keep the user from the account list', function() {
      accountListPage.getDeleteModal().cancelButton.click();

      expect(element(by.id(id.toString())).isDisplayed()).toBe(true);
    });

    it('delete buttion onclick should delete the user from the account list', function() {
      accountListPage.getDeleteModal().deleteButton.click();

      expect(element(by.id(id.toString())).isPresent()).toBe(false);
    })
  });

  it('create new account button onclick should direct to the create new account page', function() {
    accountListPage.navigateToAccountList();
    accountListPage.navigateToAddNewAccountPage();

    expect(browser.driver.getCurrentUrl()).toContain('/accounts/create/');
  });
});
