

$('#vdc-search-button').change(function() {
  var base_url = "{{ search_url }}";
  var val = $('#vdc-search').val();
  var href = $('#vdc-search-button').attr("href", base_url + val);
});
