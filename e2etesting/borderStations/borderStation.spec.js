var c = require('../testConstants.json');
var methods = require('../commonMethods.js');
var borderPage = require('./borderStation.js'); //This variable fills out the forms with test data.
var loginPage = require('../accounts/loginPage.js');
var page = this;


describe('TinyHands Border Station', function() {

	it('should have a title', function() {

		browser.manage().timeouts().implicitlyWait(5000);

        loginPage.loginAsAdmin();
        borderPage.getToBorderStationCreate();
        expect(browser.getTitle()).toContain('Border Stations');
		borderPage.fillOutBorderStation();
		borderPage.viewBorderStation();
    });

	describe('main details persist', function() {

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


		it('staff name', function(){
			borderPage.addBorderStationStaff();
			expect(element(by.id('S-firstName-0')).getAttribute('value')).toBe(c.staff0SetFirstName);
		});

		it('staff email', function(){
			expect(element(by.id("S-lastName-0")).getAttribute('value')).toBe(c.staff0SetLastName);
		});

		it('staff position', function(){
			expect(element(by.id("S-email-0")).getAttribute('value')).toBe(c.staff0Email);
		});

		it('staff phone number', function(){
			expect(element(by.id("S-phone-0")).getAttribute('value')).toBe(c.staff0Phone);
		});

		it('requires name', function(){

			expect(element(by.id("S-position-0")).getAttribute('value')).toBe(c.staff0Position);
		});

	});

});

