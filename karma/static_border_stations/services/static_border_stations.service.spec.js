
describe('BorderStationsService', function(){
    var bsService;//we'll use this scope in our tests

    //mock Application to allow us to inject our own dependencies
    beforeEach(module('BorderStationsMod'));
    //mock the controller for the same reason and include $rootScope and $controller
    beforeEach(inject(function($injector){
        //declare the controller and inject our empty scope
        bsService = $injector.get('BorderStationsService');
    }));
   
   
   describe('function createRelationship', function() {
     
   });
   
   
   
   describe('function removeRelationship', function() {
     var newValue = {};
     var newArray = [];
     var currentArray = [];
     
     beforeEach(function() {
       newValue = {
         id: 1,
         border_station: 1,
         name: 'Test Object'
       };
       currentArray = [newValue];
     });
     
     it('when value is in newArray remove it from newArray and currentArray', function() {
       // REGION: Data Setup
       newValue = { // No id to help signify it was never in DB, not req for functionality but just a reminder
         border_station: 1,
         name: 'Test Object'
       };
       newArray = [newValue];
       currentArray = [newValue];
       // ENDREGION: Data Setup
       
       bsService.removeRelationship(newValue, newArray, currentArray);
       
       expect(newArray).toEqual([]);       
       expect(currentArray).toEqual([]);       
     });
     
     it('when value is NOT in newArray call api to remove it from border station', function() {
       // REGION: Data Setup
       function fakeUpdateCall () {
         currentArray = []; // Fake removal of data
         return {
           then: function(callback) {return callback();}
         }
       }
       var apiCalls = {
         updateApiCall: function () { },
         getApiCall: function() { }
       };
       // ENDREGION: Data Setup
       
       spyOn(apiCalls,'updateApiCall').and.callFake(fakeUpdateCall);
       spyOn(apiCalls,'getApiCall');
       
       bsService.removeRelationship(newValue, newArray, currentArray, apiCalls.updateApiCall, apiCalls.getApiCall);
       
       expect(currentArray).toEqual([]);
       expect(apiCalls.updateApiCall).toHaveBeenCalled();
       expect(apiCalls.getApiCall).toHaveBeenCalled();
     });
     
     // This isnt a very good test as far as if the functionality changes whether it would break, but I couldnt find another way to do it...
     it('when updateApiFunction has errors call handleErrors', function() {
       // REGION: Data Setup
       
       var apiCalls = {
				fakeErrorHandler: function () { },
				updateApiCall: fakeUpdateCall
       };
			 
       function fakeUpdateCall () {
         currentArray = []; // Fake removal of data
         return {
           then: function() {return apiCalls.fakeErrorHandler();}
         }
       }
       // ENDREGION: Data Setup
       
       spyOn(apiCalls,'updateApiCall').and.callThrough(fakeUpdateCall);
       spyOn(apiCalls,'fakeErrorHandler');
       
       bsService.removeRelationship(newValue, newArray, currentArray, apiCalls.updateApiCall);
       
       expect(currentArray).toEqual([]);
       expect(apiCalls.fakeErrorHandler).toHaveBeenCalled();
     });
   });
   
   
   
   describe('function updateRelationship', function() {
     
   });
   
});