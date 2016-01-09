'use strict';

angular.module('AccountsMod')
  .factory('PermissionsSets', function ($resource) {
    return $resource('/api/defaultPermissionsSet/:id/', {} ,
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
