'use strict';

var constants = require('../testConstants.json');

var accountListPage = function() {
  var page = this;
  page.accounts = element.all(by.repeater('account in accountsCtrl.accounts.results'));
  page.createAccountButton = element(by.id('create'));

  this.navigateToAccountList = function() {
    return browser.get(constants.webAddress + '/accounts/');
  };

  this.navigateToEditAccountPage = function(id) {
    element(by.id(id.toString())).element(by.id('edit')).click();
  };

  this.navigateToDeleteModal = function(id) {
    element(by.id(id.toString())).element(by.buttonText('Delete')).click();
  };

  this.getDeleteModal = function() {
    var modal = {};
    modal.deleteButton = element(by.className("modal-footer")).element(by.buttonText('Delete'));
    modal.cancelButton = element(by.className("modal-footer")).element(by.buttonText('Cancel'));
    return modal;
  };

  this.navigateToAddNewAccountPage = function() {
    page.createAccountButton.click();
  };

  this.getAdminUserRow = function() {
    return page.accounts.filter(function(elem, index) {
      return elem.element(by.binding('account.email')).getText().then(function(email){
        return email == constants.adminEmail;
      });
    }).then(function(elements) {
      return elements[0];
    });
  };

};

module.exports = new accountListPage();
