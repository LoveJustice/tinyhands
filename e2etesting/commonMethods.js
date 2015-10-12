var commonMethods = function () {
    var page = this;

    this.click = function(element) {
        browser.sleep(500);
        element.click();
        browser.sleep(500);
    }
};

module.exports = new commonMethods();