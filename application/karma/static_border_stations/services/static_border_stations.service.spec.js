
describe('BorderStationsService', function(){
    var bsService;
    
    //mock Application to allow us to inject our own dependencies
    beforeEach(module('BorderStationsMod'));
    //mock the controller for the same reason and include $rootScope and $controller
    beforeEach(inject(function($injector){
      //declare the controller and inject our empty scope
      bsService = $injector.get('BorderStationsService');
    }));
   
   
   describe('function removeRelationship', function() {
     var currentArray, newArray, newValue, removeArray;
     
     beforeEach(function() {
       newValue = {
         id: 1,
         border_station: 1,
         name: 'Test Object'
       };
       currentArray = [newValue];
       newArray = [];
       newValue = {};
       removeArray = [];
     });
     
     it('should remove value from currentArray', function() {
       bsService.removeRelationship(newValue, newArray, currentArray, removeArray);
       
       expect(currentArray).toEqual([]);
     });
     
     it('when value is in newArray remove it from newArray and currentArray', function() {
       // REGION: Data Setup
       newArray = [newValue];
       // ENDREGION: Data Setup
       
       bsService.removeRelationship(newValue, newArray, currentArray, removeArray);
       
       expect(newArray).toEqual([]);
     });
     
     it('when value is NOT in newArray set border_station property to null', function() {
       bsService.removeRelationship(newValue, newArray, currentArray, removeArray);
       
       expect(newValue.border_station).toBeNull();
     });
     
     it('when value is NOT in newArray should add value to removeArray', function() {
       expect(removeArray).toEqual([]);
       
       bsService.removeRelationship(newValue, newArray, currentArray, removeArray);
       
       expect(removeArray).toEqual([newValue]);
     });
   });
   
});