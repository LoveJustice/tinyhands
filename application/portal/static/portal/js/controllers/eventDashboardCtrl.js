angular.module('PortalMod')
    .controller('EventDashboardCtrl', ['Events', '$modal', function(Events, $modal) {
        var vm = this;

        vm.days = Events.dashboard();

        vm.showEvent = function(event) {
            $modal.open({
                templateUrl: 'modal.html',
                controller: 'EventModalCtrl',
                controllerAs: 'modalCtrl',
                bindToController: true,
                resolve: {
                    event: function () {
                        return event;
                    }
                }
            })
        }
    }]);