'use strict';

angular
  .module('EventsMod')
  .controller('EditEventCtrl',['Events', '$window', '$scope', function EditEventCtrl(Events,$window,$scope) {
    var vm = this;
    vm.titleError = '';
    vm.startDateError = '';
    vm.startTimeError = '';
    vm.endDateError = '';
    vm.endTimeError = '';

    vm.format = 'yyyy-MM-dd';
    vm.start_date_popup = {
        opened: false
    };
    vm.end_date_popup = {
        opened: false
    };
    vm.end_repeat_popup = {
        opened: false
    };
    vm.start_date_open = function() {
        vm.start_date_popup.opened = true;
    };
    vm.end_date_open = function() {
        vm.end_date_popup.opened = true;
    };
    vm.end_repeat_open = function() {
        vm.end_repeat_popup.opened = true;
    };
    vm.minDate = new Date();
    vm.maxDate = new Date(2020, 5, 22);

    vm.my_start_time = new Date();
    vm.my_end_time = new Date();
    vm.display_start_time = 'n/a';
    vm.hstep = 1;
    vm.mstep = 1;
    vm.ismeridian = false;



    vm.activate = function() {


      if($window.event_id !== undefined && $window.event_id > -1) {
        vm.editing = true;
        var eventId = $window.event_id;
        Events.get({id: eventId}).$promise.then(function(event) {
            vm.event = event;
            vm.my_start_time = vm.event.start_date+'T'+vm.event.start_time;
            $scope.$watch('my_start_time', function(newValue, oldValue) {
                vm.display_start_time = moment(vm.my_start_time).format('HH:mm');
            });
        });
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
