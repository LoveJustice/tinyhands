var commonMethods = function () {
    var page = this;

    this.click = function(element) {
        browser.sleep(800);
        element.click();
        browser.sleep(800);
    }
};

module.exports = new commonMethods();