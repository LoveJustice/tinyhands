var loginPage = require('../accounts/loginPage.js');
var searchPage = require('./search.js');
var irfs = require('../dataentry/irfCRUD.js');
var vifs = require('../accounts/vifPage.js');

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
			searchPage.searchKey('TEST');
			staffName1 = element(By.xpath("//div[@class='container']/table[@class='table table-striped table-condensed']/tbody/tr[1]/td[2]"));
			expect(staffName1.getText()).toEqual('TEST');
		});

        it('shows correct vif', function () {
            searchPage.gotoVIFSearch();
            searchPage.searchKey('Test');
            staffName2 = element(By.xpath("//div[@class='container']/table[@class='table table-striped table-condensed']/tbody/tr[1]/td[2]"));
            expect(staffName2.getText()).toEqual('Test Interviewer');
        });

	});

});
