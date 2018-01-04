from django.db import models
from accounts.models import Account
from border_station import BorderStation
from country import Country
from permission import Permission
from django.conf.urls.static import static

import logging

logger = logging.getLogger(__name__);

class UserLocationPermission(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    station = models.ForeignKey(BorderStation, null=True, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    
    def match(self, other):
        if not UserLocationPermission.test_match(self.account, other.account):
            return False
        
        if not UserLocationPermission.test_match(self.country, other.country):
            return False
        
        if not UserLocationPermission.test_match(self.station, other.station):
            return False
        
        if not UserLocationPermission.test_match(self.permission, other.permission):
            return False
            
        return True;
    
    @staticmethod
    def test_match(obj1, obj2):
        if obj1 is None:
            if obj2 is not None:
                return False
        elif obj2 is None:
            return False
        elif obj1.id != obj2.id:
            return False
        
        return True
    
    @staticmethod
    def check_valid_permission_set (account_id, permission_list, permission_id, permission_group):
        check = {}
        issues = []
        for perm in permission_list:
            if perm.account.id != int(account_id):
                issues.append('account.id invalid ' + account_id + '; permission=' + str(perm.account.id))
                continue
            
            if permission_id is not None:
                if perm.permission.id != permission_id:
                    issues.append('permission.id does not match filter ' + permission_id + '; permission=' + str(perm.permission.id))
            
            if permission_group is not None:
                if perm.permission.permission_group != permission_group:
                    issues.append('permission.permission_group does not match filter ' + permission_group + '; permission=' + str(perm.permission.group))
            
            if perm.station is not None:
                key = str(perm.permission.id) + ';null;null'
                if key in check:
                    if check[key] == 'master':
                        issues.append('station conflicts with global; permission=' + str(perm))
                        continue
                else:
                    check[key] = 'parent'
                
                key = str(perm.permission.id) + ';' + str(perm.station.operating_country.id) + ';null'
                if key in check:
                    if check[key]:
                        if check[key] == 'master':
                            issues.append('station conflicts with country; permission=' + str(perm))
                            continue
                else:
                    check[key]  = 'parent'
                
                key = str(perm.permission.id) + ';' + str(perm.station.operating_country.id) + ';' + str(perm.station.id)
                if key in check:
                    issues.append('station conflicts with another station instance; permission=' + str(perm))
                    continue
                
                check[key] = 'master'
                              
            elif perm.country is not None:
                key = str(perm.permission.id) + ';null;null'
                if key in check:
                    if check[key] == 'master':
                        issues.append('country conflicts with global; permission=' + str(perm))
                        continue
                else:
                    check[key] = 'parent'
                
                key = str(perm.permission.id) + ';' + str(perm.country.id) + ';null'
                if key in check:
                    if check[key] == 'master':
                        issues.append('country conflicts with another country instance; permission=' + str(perm))
                    else:
                        issues.append('country conflicts with a station; permission=' + str(perm))
                        
                    continue
                
                check[key] = 'master'
            else:
                key = str(perm.permission.id) + ';null;null'
                if key in check:
                    if check[key] == 'master':
                        issues.append('global conflicts with another global instance; permission=' + str(perm))
                    else:
                        issues.append('global conflicts with a country or station; permission=' + str(perm))
                    continue
                
                check[key] = 'master'
                
            
        return issues
    
    @staticmethod
    def update_permission_set (account_id, new_permissions, permission_id, permission_group):
        add_permissions = {}
        remove_permissions = {}
        for perm in new_permissions:
            add_permissions[str(perm)] = perm
        
        previous_permissions = UserLocationPermission.objects.filter(account__id=account_id)
        if permission_id is not None:
            previous_permissions = previous_permissions.filter(permission__id=permission_id)
        elif permission_group is not None:
            previous_permissions = previous_permissions.filter(permission__permission_group=permission_group)
            
        for perm in previous_permissions:
            remove_permissions[str(perm)] = perm
        
        for previous in previous_permissions:
            for new in new_permissions:
                if previous.match(new):
                    remove_permissions.pop(str(previous), None)
                    add_permissions.pop(str(new), None)
        
        for perm in remove_permissions.values():
            logger.debug("removing " + str(perm))
            perm.delete()
        
        for perm in add_permissions.values():
            logger.debug("adding " + str(perm))
            perm.save();
    
    def __str__(self):
        return str(self.account) + "," + str(self.country) + "," + str(self.station) + "," + str(self.permission)