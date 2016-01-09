'use strict';

angular.module('AccountsMod')
  .factory('Accounts', function ($resource) {
    return $resource('/api/account/:id/', {} ,
      {
        me:{
          url: '/api/me',
          method: 'GET'
        },
        all: {
          url: '/api/account/all/',
          isArray : true,
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
        },
        resendActivationEmail: {
          url: '/api/account/resend-activation-email/:id/',
          method: 'POST',
          params:{
            id: '@id'
          }
        },
      }
    );
  });
