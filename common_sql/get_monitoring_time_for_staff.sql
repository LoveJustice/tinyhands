-- Used for monitor hours in the Monitor IBR
select
	"staff_id",
	staff,
	name,
	station_code,
	sum(percent_of_work)
from (
	select s.id "staff_id", s.first_name || ' ' || s.last_name "staff", c.name, bs.station_code, l."name" "location", ls.work_fraction/ss.work_days "percent_of_work"
	from
		static_border_stations_staff s join
		dataentry_locationstaff ls on ls.staff_id = s.id join
		static_border_stations_location l on l.id = ls.location_id join
		dataentry_borderstation bs on bs.id = l.border_station_id join
		dataentry_stationstatistics ss on bs.id = ss.station_id and ls.year_month = ss.year_month join
		dataentry_country c on c.id = bs.operating_country_id
	where
		ls.year_month in (202412, 202411, 202410, 202409, 202408, 202407) and
		l.location_type = 'monitoring' and
		ls.work_fraction > 0 and
		l.name != 'Leave' and
		s.last_name != '__general_staff'
) as location_staff
group by "staff_id", staff, name, station_code