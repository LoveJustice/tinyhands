describe('BorderStationsCtrl', function(){
    var vm, bsService, fakeDeferredFunction, promiseQ;//we'll use this scope in our tests
    var committeeMemTitle = 'Committee Members';
    var staffTitle = 'Staff';
    
    
    //mock Application to allow us to inject our own dependencies
    beforeEach(module('BorderStationsMod'));
    //mock the controller for the same reason and include and $controller
    beforeEach(inject(function($controller, $q, BorderStationsService){
      //declare the controller and inject our empty scope
      vm = $controller('BorderStationsCtrl');
      // declare $q
      promiseQ = $q;
      // Get service
      bsService = BorderStationsService;
    
      // Create function to fake promise
      fakeDeferredFunction = function () {
        var deferred = promiseQ.defer();
        deferred.resolve();
        return deferred.promise;
      }
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
       expect(vm.people.staff.name).toBe(staffTitle);
     });
     
     it('people committeeMembers should be an object', function() {
       expect(typeof vm.people.committeeMembers).toBe("object");
     });
     
     it('people committeeMembers name should be "Committee Members"', function() {
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
   
   
   
   describe('function createCommitteeMembers', function() {
     
     it('should call createRelationship', function() {
       spyOn(vm,'createRelationship');
       
       vm.createCommitteeMembers();
       
       expect(vm.createRelationship).toHaveBeenCalled();
     });
   });
   
   
   
   describe('function createLocations', function() {
     
     it('should call createRelationship', function() {
       spyOn(vm,'createRelationship');
       
       vm.createLocations();
       
       expect(vm.createRelationship).toHaveBeenCalled();
     });
   });
   
   
   
   describe('function createRelationship', function() {
     
     it('should call border station service createRelationship function', function() {
       spyOn(bsService, 'createRelationship').and.callFake(fakeDeferredFunction);
       
       vm.createRelationship();
       
       expect(bsService.createRelationship).toHaveBeenCalled();
     });
   });
   
   
   
   describe('function createStaff', function() {
     
     it('should call createRelationship', function() {
       spyOn(vm,'createRelationship');
       
       vm.createStaff();
       
       expect(vm.createRelationship).toHaveBeenCalled();
     });
   });
   
   
   
   describe('function handleErrors', function() {
     
     it('should add errors to errors array', function() {
      // REGION: Data Setup
      var errors = {
        data: {
          email: ['Invalid email']
        }
      };
      // ENDREGION: Data Setup
       expect(vm.errors).toEqual([]);
       
       vm.handleErrors(errors);
       
       expect(vm.errors).not.toEqual([]);
     });
   });
   
   
   
   describe('function removeCommitteeMember', function() {
     
     it('should call removeRelationship', function() {
       spyOn(vm,'removeRelationship');
       
       vm.removeCommitteeMember();
       
       expect(vm.removeRelationship).toHaveBeenCalled();
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
       // ENDREGION: Data Setup
       spyOn(vm,'removeRelationship');
       
       vm.removeLocation(location);
       
       expect(vm.removeRelationship).toHaveBeenCalled();
     });
   });
   
   
   
   describe('function removePerson', function() {
     var person, persons;
      
     beforeEach(function() {
       person = {
         removeConfirmed: true
       };
       persons = {
         name: staffTitle
       };
     });
     
     it('when person removeConfirmed is false should set person removeConfirmed to true', function() {
       // REGION: Data Setup
       person.removeConfirmed = false;
       // ENDREGION: Data Setup
       
       vm.removePerson(persons, person);
       
       expect(person.removeConfirmed).toBeTruthy();
     });
     
     it('when person removedConfirmed is true should call removeRelationship', function() {
       spyOn(vm,'removeRelationship');
       
       vm.removePerson(persons, person);
       
       expect(vm.removeRelationship).toHaveBeenCalled();
     });
     
     it('when person removedConfirmed is true and persons name is staffTitle should call removeStaff', function() {
       spyOn(vm,'removeStaff');
       
       vm.removePerson(persons, person);
       
       expect(vm.removeStaff).toHaveBeenCalled();
     });
     
     it('when person removedConfirmed is true and persons name is committeeMemTitle should call removeCommitteeMember', function() {
       // REGION: Data Setup
       persons.name = committeeMemTitle;
       // ENDREGION: Data Setup
       spyOn(vm,'removeCommitteeMember');
       
       vm.removePerson(persons, person);
       
       expect(vm.removeCommitteeMember).toHaveBeenCalled();
     });
   });
   
   
   
   describe('function removeRelationship', function() {
     
     it('should call border station service removeRelationship function', function() {
       spyOn(bsService, 'removeRelationship');
       
       vm.removeRelationship();
       
       expect(bsService.removeRelationship).toHaveBeenCalled();
     });
   });
   
   
   
   describe('function removeStaff', function() {
     
     it('should call removeRelationship', function() {
       spyOn(vm,'removeRelationship');
       
       vm.removeStaff();
       
       expect(vm.removeRelationship).toHaveBeenCalled();
     });
   });
   
   
   
   describe('function updateCommitteeMembers', function() {
     
     it('should call updateRelationship', function() {
       spyOn(vm,'updateRelationship');
       
       vm.updateCommitteeMembers();
       
       expect(vm.updateRelationship).toHaveBeenCalled();
     });
   });
   
   
   
   describe('function updateDetails', function() {
     
     it('should call updateRelationship', function() {
       // REGION: Data setup
       var details = {};
       // ENDREGION: Data setup
       spyOn(vm, 'formatDate');
       spyOn(vm,'updateRelationship');
       
       vm.updateDetails(details);
       
       expect(vm.updateRelationship).toHaveBeenCalled();
     });
   });
   
   
   
   describe('function updateLocations', function() {
     
     it('should call updateRelationship', function() {
       spyOn(vm,'updateRelationship');
       
       vm.updateLocations();
       
       expect(vm.updateRelationship).toHaveBeenCalled();
     });
   });
   
   
   
   describe('function updateRelationship', function() {
     
     it('should call border station service updateRelationship function', function() {
       spyOn(bsService, 'updateRelationship').and.callFake(fakeDeferredFunction);
       
       vm.updateRelationship();
       
       expect(bsService.updateRelationship).toHaveBeenCalled();
     });
   });
   
   
   
   describe('function updateStaff', function() {
     
     it('should call updateRelationship', function() {
       spyOn(vm,'updateRelationship');
       
       vm.updateStaff();
       
       expect(vm.updateRelationship).toHaveBeenCalled();
     });
   });
   
   
   
   describe('function updateStation', function() {
     var updateButtonText;
     
     beforeEach(function() {
       updateButtonText = 'Update Station';
       
       // Spy on all of the calls
       spyOn(vm, 'createCommitteeMembers').and.callFake(fakeDeferredFunction);
       spyOn(vm, 'createLocations').and.callFake(fakeDeferredFunction);
       spyOn(vm, 'createStaff').and.callFake(fakeDeferredFunction);
       spyOn(vm, 'updateCommitteeMembers').and.callFake(fakeDeferredFunction);
       spyOn(vm, 'updateDetails').and.callFake(fakeDeferredFunction);
       spyOn(vm, 'updateLocations').and.callFake(fakeDeferredFunction);
       spyOn(vm, 'updateStaff').and.callFake(fakeDeferredFunction);
     });
     
     it('should change updateStatusText to "Saving..."', function() {
       expect(vm.updateStatusText).toEqual(updateButtonText);
       
       vm.updateStation();
       
       expect(vm.updateStatusText).toEqual("Saving...");
     });
     
     it('should make errors array empty', function() {
       // REGION: Data Setup
       vm.errors = [{error: 'this is an error'}];
       // ENDREGION: Data Setup
       expect(vm.errors).not.toEqual([]);
       
       vm.updateStation();
       
       expect(vm.errors).toEqual([]);
     });
   });
	 
});