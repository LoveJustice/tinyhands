var commonMethods = function () {
    var page = this;

    this.click = function(element) {
        browser.sleep(500);
        element.click();
        browser.sleep(500);
    };

    this.wait = function(elementId) {
        return browser.driver.wait(function() {
            return browser.driver.findElement(by.id(elementId)).then(function(elem) {
                return element(by.id(elementId));
            });
        }, 20000);
    };
};

module.exports = new commonMethods();