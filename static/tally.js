angular.module('TallyMod',['ngCookies','ngAnimate'])
    .config(['$httpProvider', function($httpProvider) {
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    }])
    .controller('MainCtrl', ['$rootScope','$http', function($scope,$http) {
        var vm = this;

        vm.days = {};
        vm.hasIntercepts = false;
        vm.isEmptyObject = isEmptyObject;
        vm.changeColor = changeColor;

        activate();

        function activate() {
            getTallyData(true);
        }

        function isEmptyObject(obj) {
            return $.isEmptyObject(obj);
        }

        function changeColor(day) {
            if (!$.isEmptyObject(day.interceptions)) {
                return {'background-color': 'rgba(255,0,0,0.5)',
                        'color': 'rgba(255,255,255,1)'};
            }
        }

        function getTallyData(firstCall) {
            $http.get('/portal/tally/days/')
                .success(function(data) {
                // Data should be:
                // {0:{dayOfWeek:'Monday',
                //     interceptions: {<String of StationCode>:<Num of Interceptions>}},
                //  1:{dayOfWeek:'Sunday',
                //     interceptions: {...}},
                // }
                console.log(data);
                if(firstCall){
                    vm.days = data;   
                    setInterval(getTallyData, 60000);
                }else{ //updates
                    checkDifferences(data);
                }
            })
                .error(function(error) {
                console.log(error);
            });
        }
        
        function checkDifferences(data){
            for(var i = 0; i < 7; i++){
                interceptions = data[i].interceptions;
                for(var key in interceptions){
                    if(interceptions.hasOwnProperty(key)){
                        if(vm.days[i].interceptions[key] != interceptions[key]){
                            //difference found
                        }
                    }
                }
            }
            vm.days = data;
        }
    }]);
angular.bootstrap($('#tally'), ['TallyMod']);
