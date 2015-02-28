var loginPage = require('../accounts/loginPage.js');
var searchPage = require('./search.js');
var irfs = require('../irf/irfCRUD.js');

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
		it('goes to search page', function(){
			searchPage.gotoSearch();
			expect(browser.driver.getCurrentUrl()).toContain('search');
		});
	});

	it('creates irf', function(){
		irfs.getToIRF();
		irfs.fillOutIRF();
	});

	describe('result', function(){
		it('shows correct item', function(){
			searchPage.searchKey('A');
			staffName1 = element(By.xpath("//div[@class='container']/table[@class='table table-striped table-condensed']/tbody/tr[1]/td[2]"));
			expect(staffName1.getText()).toEqual('A');
		});
  
   		it('is ordered by date edited', function(){
			searchPage.searchKey('C');
			staffName2 = element(by.xpath("//div[@class='container']/table[@class='table table-striped table-condensed']/tbody/tr[1]/td[2]"));
			staffName3 = element(by.xpath("//div[@class='container']/table[@class='table table-striped table-condensed']/tbody/tr[2]/td[2]"));
			expect(staffName2.getText()).toEqual('CC');
			expect(staffName3.getText()).toEqual('CB');
		});
	});

});
