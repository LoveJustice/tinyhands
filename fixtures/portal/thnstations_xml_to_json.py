import xmltodict

with open("thnstations.kml") as f:
    xmldict = xmltodict.parse(f.read())
    outfile = open('border_stations.json', 'w')
    list_of_placemarks = xmldict['kml']['Document']['Folder']['Placemark']
    count = 1
    json_string = "[\n"
    for station in list_of_placemarks:
        both = xmldict['kml']['Document']['Folder']['Placemark'][count]['name'].split()
        name = both[0]  # take the first work which happens to be the city name
        station_code = both[1][1:-1]  # take the border station code and take off the leading and ending parenthesis
        longitude = float(xmldict['kml']['Document']['Folder']['Placemark'][count]["LookAt"]['longitude'])
        latitude = float(xmldict['kml']['Document']['Folder']['Placemark'][count]["LookAt"]['latitude'])
        json_station = ("{\n"
                       "    \"pk\": %d,\n"
                       "    \"model\": \"dataentry.borderstation\",\n"
                       "    \"fields\":{\n"
                       "        \"station_name\": \"%s\",\n"
                       "        \"station_code\": \"%s\",\n"
                       "        \"longitude\": %f,\n"
                       "        \"latitude\": %f\n"
                       "    }\n"
                       "},\n"
                       ) % (count, name, station_code, longitude, latitude)
        count += 1
        json_string += json_station
    json_string = json_string[:len(json_string)-2] + "\n]"  # this takes off the last comma and ends the json file
    outfile.write(json_string)