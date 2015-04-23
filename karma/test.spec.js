'use strict';

describe('TallyCtrl', function(){
    var vm, scope, $httpBackend;//we'll use this scope in our tests

    //mock Application to allow us to inject our own dependencies
    beforeEach(angular.module('PortalMod',['ngCookies','ngAnimate']));
    //mock the controller for the same reason and include $rootScope and $controller
    beforeEach(angular.mock.inject(function($rootScope, $controller, _$httpBackend_){
        $httpBackend = _$httpBackend_;
        // Hook http requests here

        //create an empty scope
        scope = $rootScope.$new();
        //declare the controller and inject our empty scope
        $controller('TallyCtrl', {$scope: scope});
    }));
   // tests start here

    it('should have variable days = {}', function() {
//        console.log(vm);
        expect(vm.days).toBe({});
    });

//    Example tests
//    it('should have variable text = "Hello World!"', function(){
//        expect(scope.text).toBe('Hello World!');
//    });
//    it('should fetch list of users', function(){
//        $httpBackend.flush();
//        expect(scope.users.length).toBe(2);
//        expect(scope.users[0].name).toBe('Bob');
//    });
});
