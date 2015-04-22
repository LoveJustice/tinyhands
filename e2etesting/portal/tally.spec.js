var tallyHelper = require('./tally');
var loginPage = require('../accounts/loginPage');
var irfCrud = require('../irf/irfCRUD');

describe('Tally UI', function(){
    beforeEach(function () {
        return browser.ignoreSynchronization = true;
    });
    
    it('should have 7 days on screen', function(){
        browser.sleep(1000);
        loginPage.loginAsAdmin();
        tallyHelper.navigateHome();
        var days = element.all(by.css('.day-of-week')).filter(function(elem, index) {
            return elem.isDisplayed();
        });
        expect(days.count()).toEqual(7);
        
    });
    
    it('should have no interceptions for the 7 days', function(){
        var daysText = element.all(by.css('h4.animated.tallyFade'));
        daysText.each(function(element, index){
            element.getInnerHtml().then(function(text){
                expect(text).toEqual('No Interceptions');
            });
        });
    });
    
    it('should list interceptions when there are some', function() {
        irfCrud.getToIRF().then(function(){
            expect(browser.driver.getCurrentUrl()).toContain('data-entry/irfs/create/');
            var date = new Date();
            irfCrud.fillOutIRF(new Date().toString());
            browser.sleep(10000);
            return tallyHelper.navigateHome();
            
        }).then(function(){
            var days = element.all(by.css('.day-of-week')).filter(function(elem, index) {
                return elem.isDisplayed();
            });
            expect(days.count()).toEqual(7);
            
            var interceptions = element.all(by.css('h4.animated.tallyFade')).filter(function(elem, index) {
                return elem.getInnerHtml().then(function(text){
                    return text != 'No Interceptions';
                });
            });
            
            expect(interceptions.count()).toEqual(1);
            expect(interceptions.first().getInnerHtml()).toEqual('1 INT in BHD');
        });
    });
    
     
});