from dataentry.models import District, VDC

geofile = open("/home/dustin/studio/tinyhands/bin/locations.txt")

for aline in geofile:
	aline=aline.replace("\n","")
	v=aline.split("\t")
	if District.objects.filter(name=v[0]) is None:
		print "district_name" + v[0]
		district=District(district_name=v[0])
		district.save()
	if VDC.objects.filter(name=v[1]) is None:
		print "name " + v[1]
		print "lat " + v[3]
		print "long " + v[4]
		print "district" + v[0]
		print "cannonical is null"
		vdc=VDC(name=v[1],latitude=v[3],longitude=[4],district=v[0])
		vdc.save()
	if v[2] and VDC.objects.filter(name=v[2]) is None:
		print "name " + v[2]
		print "lat " + v[3]
		print "long " + v[4]
		print "district " + v[0]
		print "cannonical name is " + v[1]
		vdc=VDC(name=v[2],latitude=v[3],longitude=[4],district=v[0],cannonical_name=v[1])
		vdc.save()
