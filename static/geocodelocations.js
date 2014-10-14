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

            if(!$('.popover').hasClass('in'))
                {
                $(this).popover('show');
            }

            input = $(element).val();
            if(element.id.indexOf("district") > 0){
                callFuzzyApi(input, "district");
            }else{
                callFuzzyApi(input, "vdc");
            }
	    });
	});
}

function callFuzzyApi(input, locationType){
    var unorderedList = $("#popover-location-info");
    
    if(input !== ""){
	$.ajax({
	    url: "/data-entry/geocodelocation/"+locationType+"/",
	    data: locationType+"="+input,
	}).done(function(data){
        unorderedList.empty();
        console.log(data);
        if (data.id != -1) {
            for (i in data) {
                unorderedList.append($('<div></div>').append(data[i].name));
            }
            console.log(unorderedList);
        }
	});
     }
}

setPopovers("[id$=address_district]");
setPopovers("[id$=address_vdc]");
setPopovers("[id$=-vdc]");
setPopovers("[id$=-district]");