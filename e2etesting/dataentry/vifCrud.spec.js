var crudPage = require('./vifCrud.js');
var c = require('../testConstants.json');
var loginPage = require('../accounts/loginPage.js');


describe('VIF CRUD -', function() {

    beforeEach(function () {
        return browser.ignoreSynchronization = true;
    });

    describe('A user', function () {

        it('Logs In', function () {
            loginPage.logout();
            loginPage.loginAsAdmin();
            browser.get(c.webAddress + "/data-entry/vifs/");
            browser.sleep(4000);
        });

        it('should have a title', function () {
            browser.get(c.webAddress + "/data-entry/vifs/create/");
            expect(browser.getTitle()).toContain('Create VIF');
        });

        describe('properly filled out form can be created and is created and shows up in the VIF page.', function () {
            it('creates and submits a new vif, causing it to show up on the "vif" page', function () {
                crudPage.completeVif();
                browser.get(c.webAddress + "/data-entry/vifs");
                expect(element(by.id("id_vif_list_table")).isPresent()).toBe(true);
            });
        });

        describe('submitted vif can be reviewed', function () {
            it('reviews a created vif form and checks that the data is still the same', function () {
                crudPage.checkEditedVif();
                browser.sleep(4000);
                expect(element(by.id("id_vif_number")).getAttribute('value')).toContain(c.vifNumber);
            });
        });

        describe('edited vif should be able to be submitted and remain edited when viewed', function () {
            it('edits a vif and checks to see that the changed value stays changed', function () {
                crudPage.editVif();
                crudPage.checkEditedVif();
                browser.sleep(800);
                expect(element(by.id("id_vif_number")).getAttribute('value')).toContain(c.vifNumber);
            });
        });

        describe('if you edit a vif and leave one of the required fields empty, you should not be able to submit it', function () {
            it('edits a vif and leaves a required field unfilled', function () {
                browser.get(c.webAddress + "/data-entry/vifs");
                crudPage.incorrectly_edit_vif();
                browser.sleep(5000);
                expect(element(by.id("error-box")).isPresent()).toBe(true);
            });
        });
        describe('if you enter vif number with correct station code, the interviewer dropdown should include staff from that station', function () {
            it ('enters vif number and checks dropdown for staff associated to station', function () {
                browser.get(c.webAddress + "/data-entry/vifs");
                crudPage.good_vif_staff_dropdown();
                expect(element(by.xpath('//span[text()="SFname0 SLname0"]')))
            });
        });
        describe('if you enter vif number with a non-existent station code, the interviewer dropdown will say Invalid Station Code', function () {
            it ('enters non-existent code and checks dropdown for Invalid Station Code message', function () {
                browser.get(c.webAddress + "/data-entry/vifs");
                crudPage.bad_vif_staff_dropdown();
                expect(element(by.xpath('//span[text()="Invalid Station Code"]')))
            });
        });
    });
});