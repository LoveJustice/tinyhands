var tallyHelper = require('./tally');
var loginPage = require('../accounts/loginPage');
var irfCrud = require('../irf/irfCRUD');

describe('Tally UI', function(){
    beforeEach(function () {
        return browser.ignoreSynchronization = true;
    });
    
    it('should have 7 days on screen', function(){
        browser.driver.manage().window().maximize();
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
    
    it('should auto update every minute', function() {
        browser.driver.executeScript(function() { //open new tab
          (function(a){
          document.body.appendChild(a);
          a.setAttribute('href',"http://0.0.0.0:8001" );
          a.dispatchEvent((function(e){
            e.initMouseEvent("click", true, true, window, 0, 0, 0, 0, 0, true, false, false, false, 0, null);
            return e;
          }(document.createEvent('MouseEvents'))))}(document.createElement('a')));
        }).then(function () { // switch to the newly created tab
            return browser.getAllWindowHandles().then(function (handles) {
                newWindowHandle = handles[1];
                return browser.switchTo().window(newWindowHandle);
            });
        }).then(function() { // complete new irf
            return irfCrud.getToIRF().then(function(){
                expect(browser.driver.getCurrentUrl()).toContain('data-entry/irfs/create/');
                var date = new Date();
                irfCrud.fillOutIRF(new Date().toString());
                return tallyHelper.navigateHome();
            });
        }).then(function() { //close second tab and return back to first tab
            return browser.driver.close().then(function () {
                return browser.getAllWindowHandles().then(function (handles) {
                    newWindowHandle = handles[0];
                    return browser.switchTo().window(newWindowHandle);
                });
            });
        }).then(function() { //wait one minute for update to occur
            return browser.sleep(60000);
        }).then(function () {
            var interceptions = element.all(by.css('h4.animated.tallyFade')).filter(function(elem, index) {
                return elem.getInnerHtml().then(function(text){
                    return text != 'No Interceptions';
                });
            });
            
            expect(interceptions.count()).toEqual(1);
            expect(interceptions.first().getInnerHtml()).toEqual('2 INT in BHD');
            var tab = interceptions.first().element(by.xpath('..')).element(by.xpath('..'));
            expect(tab.getCssValue('color')).toEqual('rgba(255, 255, 255, 1)');
            //expect(tab.getCssValue('background-color')).toEqual('rgba(255, 0, 0, 0.5)');
        });
    }, 90000);
    
     
});