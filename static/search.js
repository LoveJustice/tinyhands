$('#vdc-search').keypress(function(e) {

  if(e.which == 13)
  {
    var val = $('#vdc-search').val();
    $("#vdc-search-button").attr("href", "/data-entry/geocodelocations/vdc-admin/search/" + val);
    $("#vdc-search-button")[0].click();
  }

});
