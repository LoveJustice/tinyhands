$(document).ready(function() {
  $('.crud-datatable').dataTable( {
    /*
     * -JS- Use -1 to be more agile. http://stackoverflow.com/a/7659254/5020352
     */
    "aoColumnDefs": [{"bSortable": false, "aTargets": [-1],}],
    "bFilter": true,
    "bInfo": false,
    "bPaginate": true,
  });
});

//For VDC and District admin pages, create modal functionality
$("*[id*=update_link]:visible").each(
    function() {
        $(this).click(
            function(e){
                e.preventDefault();
                $("#modal").load(this.href, function(){$("#modal").modal("show");
        });
    });
});
