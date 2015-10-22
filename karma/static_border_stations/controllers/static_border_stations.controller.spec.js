describe('BorderStationsCtrl', function(){
    var vm;//we'll use this scope in our tests

    //mock Application to allow us to inject our own dependencies
    beforeEach(module('BorderStationsMod'));
    //mock the controller for the same reason and include $rootScope and $controller
    beforeEach(inject(function($controller){
        //declare the controller and inject our empty scope
        vm = $controller('BorderStationsCtrl');
    }));
   
   
   describe('initial value', function() {
     it('borderStationId should be equal to window border_station_pk', inject(function($controller) {
       // REGION: Data Setup
       window.border_station_pk = 116;
       
       var theCtrl = $controller('BorderStationsCtrl');
       // ENDREGION: Data Setup
       
       expect(theCtrl.borderStationId).toBe(window.border_station_pk);
     }));
     
     it('details should be an empty object', function() {
       expect(vm.details).toEqual({});
     });
     
     it('errors should be an empty array', function() {
       expect(vm.errors).toEqual([]);
     });
     
     it('locations should be an empty array', function() {
       expect(vm.locations).toEqual([]);
     });
     
     it('newCommitteeMembers should be an empty array', function() {
       expect(vm.newCommitteeMembers).toEqual([]);
     });
     
     it('newLocations should be an empty array', function() {
       expect(vm.newLocations).toEqual([]);
     });
     
     it('newStaff should be an empty array', function() {
       expect(vm.newStaff).toEqual([]);
     });
     
     it('people should be an object', function() {
       expect(typeof vm.people).toBe("object");
     });
     
     it('people staff should be an object', function() {
       expect(typeof vm.people.staff).toBe("object");
     });
     
     it('people staff name should be "Staff"', function() {
       // REGION: Data Setup
       var staffTitle = 'Staff';
       // ENDREGION: Data Setup
       expect(vm.people.staff.name).toBe(staffTitle);
     });
     
     it('people committeeMembers should be an object', function() {
       expect(typeof vm.people.committeeMembers).toBe("object");
     });
     
     it('people committeeMembers name should be "Committee Members"', function() {
       // REGION: Data Setup
       var committeeMemTitle = 'Committee Members';
       // ENDREGION: Data Setup
       expect(vm.people.committeeMembers.name).toBe(committeeMemTitle);
     });
     
     it('updateStatusText should be "Update Station"', function() {
       // REGION: Data Setup
       var updateButtonText = 'Update Station';
       // ENDREGION: Data Setup
       expect(vm.updateStatusText).toBe(updateButtonText);
     });
   });
   
	 
	 describe('function addLocation', function() {
     
     beforeEach(function() {
       vm.borderStationId = 1; // Fake border station id
       vm.newLocations = []; // Empty array that holds new locations
       vm.locations = []; // Empty array that holds all locations
     });
     
     it('should add new object to newLocations with border_station set to borderstation id', function() {
       expect(vm.newLocations).toEqual([]);
       
       vm.addLocation();
       
       expect(vm.newLocations).toContain({border_station: 1});
     });
     
     it('should add new object to newLocations with border_station set to borderstation id', function() {
       expect(vm.locations).toEqual([]);
       
       vm.addLocation();
       
       expect(vm.locations).toContain({border_station: 1});
     });
   });
	 
	 
	 describe('function addPerson', function() {
     
     var committeeMemTitle = 'Committee Members';
     var staffTitle = 'Staff';
     
     var emptyPerson = {border_station: 1};
     
     beforeEach(function() {
       vm.borderStationId = 1; // Fake border station id
       vm.newCommitteeMembers = []; // Empty array that holds new committee members
       vm.newStaff = []; // Empty array that holds new staff
       vm.people = { // Empty object that holds all people
         staff: {
           name: staffTitle,
           data: []
         },
         committeeMembers: {
           name: committeeMemTitle,
           data: []
         }
       };
     });
     
     it('when persons name is staffTitle should add new person to newStaff', function() {
       expect(vm.newStaff).toEqual([]);
       
       vm.addPerson({name: staffTitle});
       
       expect(vm.newStaff).toContain(emptyPerson);
     });
     
     it('when persons name is staffTitle should add new person to people staff data', function() {
       expect(vm.people.staff.data).toEqual([]);
       
       vm.addPerson({name: staffTitle});
       
       expect(vm.people.staff.data).toContain(emptyPerson);
     });
     
     it('when persons name is committeeMemTitle should add new person to newCommitteeMembers', function() {
       expect(vm.newCommitteeMembers).toEqual([]);
       
       vm.addPerson({name: committeeMemTitle});
       
       expect(vm.newCommitteeMembers).toContain(emptyPerson);
     });
     
     it('when persons name is committeeMemTitle should add new person to people committeeMembers data', function() {
       expect(vm.people.committeeMembers.data).toEqual([]);
       
       vm.addPerson({name: committeeMemTitle});
       
       expect(vm.people.committeeMembers.data).toContain(emptyPerson);
     });
   });
   
   
   describe('function changeStationStatus', function() {
     it('should toggle open status from false to true for a station', function() {
       // REGION: Data Setup
       vm.details.open = false;
       // ENDREGION: Data Setup
       
       vm.changeStationStatus();
       
       expect(vm.details.open).toBeTruthy();
     });
     
     it('should toggle open status from true to false for a station', function() {
       // REGION: Data Setup
       vm.details.open = true;
       // ENDREGION: Data Setup
       
       vm.changeStationStatus();
       
       expect(vm.details.open).toBeFalsy();
     });
   });
   
   
   
   describe('function removeLocation', function() {
     it('when location removedConfirmed is false should set location removedConfirmed to true', function() {
       // REGION: Data Setup
       var location = {
         removeConfirmed: false
       }
       // ENDREGION: Data Setup
       
       vm.removeLocation(location);
       
       expect(location.removeConfirmed).toBeTruthy();
     });
     
     it('when location removedConfirmed is true should call removeRelationship', function() {
       // REGION: Data Setup
       var location = {
         removeConfirmed: true
       }
       spyOn(vm,'removeRelationship');
       // ENDREGION: Data Setup
       
       vm.removeLocation(location);
       
       expect(vm.removeRelationship).toHaveBeenCalled();
     });
   });
   
   
   
   describe('function removePerson', function() {
     var staffTitle = 'Staff';
     
     it('when person removeConfirmed is false should set person removeConfirmed to true', function() {
       // REGION: Data Setup
       var persons = {};
       var person = {
         removeConfirmed: false
       }
       // ENDREGION: Data Setup
       
       vm.removePerson(persons, person);
       
       expect(person.removeConfirmed).toBeTruthy();
     });
     
     it('when person removedConfirmed is true should call removeRelationship', function() {
       // REGION: Data Setup
       var persons = {
         name: staffTitle
       };
       var person = {
         removeConfirmed: true
       }
       spyOn(vm,'removeRelationship');
       // ENDREGION: Data Setup
       
       vm.removePerson(persons, person);
       
       expect(vm.removeRelationship).toHaveBeenCalled();
     });
   });
   
   
   
   describe('function removeRelationship', function() {
     it('when value is in newArray remove it from newArray and currentArray', function() {
       // REGION: Data Setup
       var newValue = {
         border_station: 1,
         name: 'Test Object'
       };
       var newArray = [newValue];
       var currentArray = [newValue];
       // ENDREGION: Data Setup
       
       vm.removeRelationship(newValue, newArray, currentArray);
       
       expect(newArray).toEqual([]);       
       expect(currentArray).toEqual([]);       
     });
   });
   
   
   
   describe('function updateRelationship', function() {
     
   });
   
   
   
   describe('function updateStation', function() {
     
   });
	 
});