var loginPage = require('../accounts/loginPage.js');
var searchPage = require('./search.js');
var irfs = require('../dataentry/irfCRUD.js');
var vifs = require('../dataentry/vifPage.js');
var c = require('../testConstants.json');

describe('TinyHands', function(){

	beforeEach(function(){
		return browser.ignoreSynchronization = true;
	});

	describe('admin can login', function(){
		it('accepts credentials', function(){
			loginPage.loginAsAdmin();
			expect(browser.driver.getCurrentUrl()).toContain('portal/dashboard');
		});
	});

	describe('navigation', function(){
		it('goes to IRF search page', function(){
			irfs.getToIRF();
			irfs.fillOutIRF(c.irfNumber);
            searchPage.gotoIRFSearch();
			expect(browser.driver.getCurrentUrl()).toContain('irfs');
		});

        it('goes to VIF search page', function(){
			searchPage.gotoVIFSearch();
			expect(browser.driver.getCurrentUrl()).toContain('vifs');
		});
	});

	describe('result', function(){
		it('shows correct irf', function(){
            searchPage.gotoIRFSearch();
			searchPage.searchKey('TEST', "vm.searchValue");
			staffName1 = element(By.xpath('//*[@id="content-container"]/div/table/tbody/tr[1]/td[2]'));

			expect(staffName1.getText()).toEqual('TEST');
		});

        it('shows correct vif', function () {
            searchPage.gotoVIFSearch();

            searchPage.searchKey('TEST', "vm.searchValue");
			staffName2 = element(By.xpath('//*[@id="id_vif_list_table"]/tbody/tr[1]/td[2]'));
            expect(staffName2.getText()).toEqual('Test Interviewer');
        });

	});

});
