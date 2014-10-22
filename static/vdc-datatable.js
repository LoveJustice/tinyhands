$(document).ready( function() {
  $('#vdc_table').dataTable( {
    "aoColumnDefs": [
      { "bSortable": false, "aTargets": [ 6 ] }
    ],
    "bFilter": false, 
    "bInfo": false,
    "bPaginate": false,
	} );
} );