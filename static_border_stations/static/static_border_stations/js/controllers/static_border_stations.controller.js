(function() {
	'use strict';
	
	angular.module('BorderStationsMod')
		.controller('BorderStationsCtrl', BorderStationsCtrl);
		
	BorderStationsCtrl.$inject = ['BorderStationsService'];
		
	function BorderStationsCtrl(BorderStationsService) {
		var vm = this;
		
		vm.details = {};
		
		activate();
		
		function activate() {
			getBorderstation();
		}
		
		function getBorderstation() {
			BorderStationsService.getStation(0).then(function(data) {
				vm.details = data.data;
			});
		}
	}
})();