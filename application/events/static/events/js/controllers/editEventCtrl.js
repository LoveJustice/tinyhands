'use strict';

angular
  .module('EventsMod')
  .controller('EditEventCtrl', EditEventCtrl)

  EditEventCtrl.$inject = ['Events',$window]

  function EditEventCtrl(Events,$window) {
    var vm = this;

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
  }
