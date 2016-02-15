angular
  .module('EventsMod')
  .controller('EventsCtrl', ['Events', '$modal', function(Events, $modal) {
    var vm = this;

    vm.activate = function () {
      vm.events = Events.all();
    }

    vm.openModal = function(event) {
      var eventTitle = event.title;
      var deleteModal = $modal.open({
        templateUrl: 'modal.html',
        controller: 'ModalCtrl',
        controllerAs: 'modalCtrl',
        resolve: {
          eventTitle: function() {
            return eventTitle;
          }
        }
      });
      deleteModal.result.then( function() {
        Events.destroy({id: event.id}).$promise.then( function() {
          vm.events = Events.all()
        }
      })
    }

    vm.activate();
  }]);
