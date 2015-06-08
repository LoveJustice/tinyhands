from dataentry.models import District, VDC

geofile = open("/home/dustin/studio/tinyhands/bin/locations.txt")
# This file was done entirely by Dustin, but seems like it won't work globally because of ^.

for aline in geofile:
    aline = aline.replace("\n", "")
    v = aline.split("\t")
    # Check district
    if not District.objects.filter(name=v[0]):
        district = District(name=v[0])
        district.save()
    # Check cannonical vdc
    if not VDC.objects.filter(name=v[1]):
        d = District.objects.filter(name=v[0])[0]
        vdc = VDC(name=v[1], latitude=float(v[3]), longitude=float(v[4]), district=d)
        vdc.save()
    # Check alternate name of vdc
    if v[2]:
        x = VDC.objects.filter(name=v[1])[0]
        d = District.objects.filter(name=v[0])[0]
        vdc = VDC(name=v[2], latitude=float(v[3]), longitude=float(v[4]), district=d, cannonical_name=x)
        vdc.save()
