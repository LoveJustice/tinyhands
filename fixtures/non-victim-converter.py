import json
import csv

csvFile = open("../fixtures/nvids.csv", 'r')
result = {}

fieldnames = ("Date", "Case #", "Name", "Original Name", 
              "Last Name", "Age", "District", "VDC/City",
              "Phone", "Original Phone", "Gender",
              "Occupation", "Caste", "2nd Phone")

reader = csv.DictReader(csvFile, fieldnames)

for row in reader:
    print(row)
    
    #write:
    
    """
    {
        fields: {
            \"%s\":
        }
    
    """


    {
    "pk": 7,
    "model": "accounts.account",
    "fields": {
        "groups": [],
        "first_name": "Andrew",
        "last_name": "Smith",
        "permission_accounts_manage": true,
        "permission_irf_add": true,
        "permission_irf_view": true,
        "user_designation": 1,
        "is_active": true,
        "permission_vif_add": true,
        "permission_vif_view": true,
        "permission_vif_edit": true,
        "is_superuser": true,
        "is_staff": true,
        "last_login": "2014-05-05T13:25:25.906Z",
        "date_joined": "2014-04-16T17:23:25.607Z",
        "user_permissions": [],
        "password": "pbkdf2_sha256$12000$08ATKEmg0hpl$szBXuVriGgTVuJSTPx2D+wmzOl2evJAjwXsa0ben76Q=",
        "email": "andrew_smith3@taylor.edu",
        "permission_irf_edit": true,
        "permission_receive_email": false,
        "permission_border_stations_view": true,
        "permission_border_stations_add": true,
        "permission_border_stations_edit": true,
        "permission_vdc_manage":true
    }
},
    
{
    "pk" : 1,
    "model": "
    "Date":"3/8/2013",
    "Case #":"OSI077",
    "Name":"Yuwak (Yubak) Theeng Lama",
    "Original Name":"Yubak Lama",
    "Last Name":"Lama",
    "Age":"",
    "District":"",
    "VDC/City":"",
    "Phone":"",
    "Original Phone":"",
    "Gender":"",
    "Occupation":"",
    "Caste":"",
    "2nd Phone":""
  },