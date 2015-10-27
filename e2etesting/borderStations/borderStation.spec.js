var c = require('../testConstants.json');
var methods = require('../commonMethods.js');
var borderStationForm = require('./borderStation.js') //This variable fills out the forms with test data.
var page = this;


describe('TinyHands Border Station', function() {
	
	describe('details persist', function() {
		it('station name should persist', function(){
			expect(element(by.id('stationName')).getText().toBe())	
		});
		
		it('station code should persist', function(){
			expect(element(by.id('stationName')).getText().toBe())
		});
	
		it('date established should persist', function(){
			expect(element(by.id('dateEstablished')).getText().toBe())	
		});
		
		it('latitude should persist', function(){
			expect(element(by.id('latitude')).getAttribute("value").toBe('100'));			
		});

		it('longitude should persist', function(){
			expect(element(by.id('longitude')).getAttribute("value").toBe('200'));	
		});
	});
});

