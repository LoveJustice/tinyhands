'use strict';

angular.module('AccountsMod')
  .factory('Accounts', function ($resource) {
    return $resource('/api/accounts/:id/', {} ,
      {
        all: {
          method: 'GET'
        },
        get: {
          method: 'GET',
          params: {
            id: '@id'
          }
        },
        create: {
          method: 'POST'
        },
        update: {
          method: 'PUT',
          params:{
            id: '@id'
          }
        },
        destroy: {
          method: 'DELETE',
          params:{
            id: '@id'
          }
        }
      }
    );
  });
