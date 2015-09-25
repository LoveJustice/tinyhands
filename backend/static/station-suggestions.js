function stationSuggestion(id){
    
    $.ajax({
	url:"/data-entry/stations/codes/"
    }).done(function (data){
	var codes = data;
	$(id).autocomplete({source: codes})
    });
}

stationSuggestion("#formSearchBox");
