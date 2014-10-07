function setPopovers(id)
{
	$(id).each(function(index, element) {
	    $(element).popover({
	        content: $("#geocode-form").html(),
	        html:true,
	        placement:'bottom',
	        container: 'body',
	    });
	    $(element).blur(function() {
	    	if($('.popover').hasClass('in'))
	    	{
		    	$(this).popover('hide');
			}	
	    });
	    $(element).keyup(function(){
        var unorderedList = $("#popover-location-info");
        unorderedList.empty();
            
		if(!$('.popover').hasClass('in'))
	    	{
		    $(this).popover('show');
		}
		
		input = $(element).val();
		if(input !== ""){
		    $.ajax({
			url: "/data-entry/geocodelocation/district/",
			data: "district="+input,
			
		    }).done(function(data){
                console.log(data);
                if (data.id != -1) {
                    for (i in data) {
                        unorderedList.append($('<div></div>').append(data[i].name));
                    }
                    console.log(unorderedList);
                }
		    });
		}
		
	    });
	});
}
setPopovers("#id_location");
setPopovers("[id$=address_district]");
setPopovers("[id$=address_vdc]");
setPopovers("[id$=-vdc]");
setPopovers("[id$=-district]");
