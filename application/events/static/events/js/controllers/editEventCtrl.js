'use strict';

angular
  .module('EventsMod')
  .controller('EditEventCtrl',['Events', '$window', function EditEventCtrl(Events,$window) {
    var vm = this;
    vm.titleError = '';
    vm.startDateError = '';
    vm.startTimeError = '';
    vm.endDateError = '';
    vm.endTimeError = '';

    vm.format = 'yyyy-MM-dd';

    vm.popup1 = {
        opened: false
    };
    vm.popup2 = {
        opened: false
    };
    vm.popup3 = {
        opened: false
    };

    vm.open1 = function() {
        vm.popup1.opened = true;
    };
    vm.open2 = function() {
        vm.popup2.opened = true;
    };
    vm.open3 = function() {
        vm.popup3.opened = true;
    };

    

    vm.minDate = new Date();
    vm.maxDate = new Date(2020, 5, 22);

    vm.activate = function() {


      if($window.event_id !== undefined && $window.event_id > -1) {
        vm.editing = true;
        var eventId = $window.event_id;
        vm.event = Events.get({id: eventId});
      } else {
        vm.editing = false;
        vm.event = {
          title: '',
          location: '',
          start_date: '',
          start_time: '',
          end_date: '',
          end_time: '',
          description: '',
          is_repeat: false,
          repetition: '',
          ends: '',
        }
      }
    }

    vm.update = function() {
      if(!vm.checkFields()) {
        return;
      }
      var call;
      if(vm.editing) {
        call = Events.update(vm.event).$promise;
      }else {
        call = Events.create(vm.event).$promise;
      }
      call.then(function() {
        $window.location.href = '/events/list/';
      }, function(err) {
        if(err.data.title) {
          vm.titleError = err.data.title[0];
          vm.startDateError = err.data.title[1];
          vm.startTimeError = err.data.title[2];
          vm.endDateError = err.data.title[3];
          vm.endTimeError = err.data.title[4];
        }
      });
    }

    vm.checkFields = function() {
      vm.titleError = '';
      vm.startDateError = '';
      vm.startTimeError = '';
      vm.endDateError = '';
      vm.endTimeError = '';
      if(!vm.event.title) {
        vm.titleError = 'Title field is required';
      }
      if(!vm.event.start_date) {
        vm.startDateError = 'Start date field is required';
      }
      if(!vm.event.start_time) {
        vm.startTimeError = 'Start time field is required';
      }
      if(!vm.event.end_date) {
        vm.endDateError = 'End date field is required';
      }
      if(!vm.event.end_time) {
        vm.endTimeError = 'End time field is required';
      }
      if(vm.titleError || vm.startDateError || vm.startTimeError || vm.endDateError || vm.endTimeError) {
        return false;
      }
      return true
    }

    vm.getTitle = function() {
      if(vm.editing) {
        return 'Edit Event';
      }
      return 'Create Event';
    }

    vm.activate();
}]);
