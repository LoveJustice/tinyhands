var c = require('../testConstants.json');
var methods = require('../commonMethods.js');
var borderPage = require('./borderStation.js'); //This variable fills out the forms with test data.
var loginPage = require('../accounts/loginPage.js');
var page = this;


describe('TinyHands Border Station', function() {

	beforeEach(function() {
		browser.ignoreSynchronization = true;
		browser.manage().timeouts().implicitlyWait(7000);
	});

	it('should have a title', function() {

		//browser.manage().timeouts().implicitlyWait(10000);

        loginPage.loginAsAdmin();
        borderPage.getToBorderStationCreate();
		browser.sleep(1000);
        expect(browser.getTitle()).toContain('Border Stations');
		borderPage.fillOutBorderStation(c.stationName, c.stationCode);
		browser.sleep(500);
		borderPage.viewBorderStation();
    });

	describe('main details persist', function() {

		//browser.ignoreSynchronization = false;

		it('station name should persist', function(){				
			expect(element(by.id('stationName')).getAttribute('value')).toBe(c.stationName);
		});

		it('station code should persist', function(){
			expect(element(by.id('stationCode')).getAttribute('value')).toBe(c.stationCode);
		});

		it('date established should persist', function(){
			expect(element(by.id('dateEstablished')).getAttribute('value')).toBe("2001-01-01");
		});

		it('latitude should persist', function(){
			expect(element(by.id('latitude')).getAttribute("value")).toBe('0');
		});

		it('longitude should persist', function(){
			expect(element(by.id('longitude')).getAttribute("value")).toBe('0');
		});
	});

	describe('staff details persist', function() {

		//browser.ignoreSynchronization = false;

		it('staff name', function(){
			borderPage.addBorderStationStaff();
			expect(element(by.id('S-firstName-0')).getAttribute('value')).toBe(c.staff0SetFirstName);
		});

		it('staff email', function(){
			browser.wait(protractor.ExpectedConditions.presenceOf(element(by.id('S-lastName-0'))), 7000);
			expect(element(by.id("S-lastName-0")).getAttribute('value')).toBe(c.staff0SetLastName);
			//browser.driver.wait(function() {
			//	return browser.driver.findElement(by.id('S-lastName-0')).then(function(elem) {
			//		expect(element(by.id("S-lastName-0")).getAttribute('value')).toBe(c.staff0SetLastName);
			//		return true;
			//	});
			//}, 20000);
		});

		it('staff position', function(){
			browser.wait(protractor.ExpectedConditions.presenceOf(element(by.id('S-email-0'))), 7000);
			expect(element(by.id("S-email-0")).getAttribute('value')).toBe(c.staff0Email);
		});

		it('staff phone number', function(){
			expect(element(by.id("S-phone-0")).getAttribute('value')).toBe(c.staff0Phone);
		});

		it('requires name', function(){
			expect(element(by.id("S-position-0")).getAttribute('value')).toBe(c.staff0Position);
		});

	});

	describe('committee details persist', function() {

		//browser.ignoreSynchronization = false;

		it('committee name', function(){
			borderPage.addBorderStationCommitteeMember();
			expect(element(by.id('C-firstName-0')).getAttribute('value')).toBe(c.staff0SetFirstName);
		});

		it('committee email', function(){
			browser.wait(protractor.ExpectedConditions.presenceOf(element(by.id('C-email-0'))), 7000);
			expect(element(by.id("C-email-0")).getAttribute('value')).toBe(c.staff0Email);
		});

		it('committee position', function(){
			browser.wait(protractor.ExpectedConditions.presenceOf(element(by.id('C-email-0'))), 7000);
			expect(element(by.id("C-email-0")).getAttribute('value')).toBe(c.staff0Email);
		});

		it('committee phone number', function(){
			expect(element(by.id("C-phone-0")).getAttribute('value')).toBe(c.staff0Phone);
		});

		it('requires name', function(){

			expect(element(by.id("C-position-0")).getAttribute('value')).toBe(c.staff0Position);
		});

	});

	describe('location details persist', function() {

		//browser.ignoreSynchronization = false;

		it('location name', function(){
			borderPage.addBorderStationLocation();
			expect(element(by.id('locationName-0')).getAttribute('value')).toBe(c.location0SetName);
		});

		it('location latitude', function(){
			browser.wait(protractor.ExpectedConditions.presenceOf(element(by.id('latitude-0'))), 7000);
		//	browser.driver.wait(function() {
		//		return browser.driver.findElement(by.id('latitude-0')).then(function(elem) {
			expect(element(by.id("latitude-0")).getAttribute('value')).toBe(c.location0SetLatitude);
		//			return true;
		//		});
		//	}, 20000);
		});

		it('location longitude', function(){
			browser.wait(protractor.ExpectedConditions.presenceOf(element(by.id('latitude-0'))), 7000);
			expect(element(by.id("longitude-0")).getAttribute('value')).toBe('0');
		});

	});

});

