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
		console.log("Testing...");

            if(!$('.popover').hasClass('in'))
                {
                $(this).popover('show');
            }

            input = $(element).val();
            if(element.id.indexOf("district") > 0){
                var fuzzyText = callFuzzyApi(input, "district", element);
            }else{
                var fuzzyText = callFuzzyApi(input, "vdc", element);
	    }
	    });
	});
}

function callFuzzyApi(input, locationType, element){
    var unorderedList = $("#popover-location-info");
    if(input !== ""){
	$.ajax({
	    url: "/data-entry/geocodelocation/"+locationType+"/",
	    data: locationType+"="+input,
	}).done(function(data){
            unorderedList.empty();
            //console.log(data);
            if (data.id != -1) {
		for (i in data) {
		    //Add event for these divs that will extract the text from the div
		    unorderedList.append($('<div class="btn fuzzymatches"></div>').append(data[i].name));
		    unorderedList.find(".fuzzymatches").each(function(){
                $(this).click(function() {
                    $(element).val($(this).text());
                }).css('cursor','pointer');
                $(this).hover(function(e) {
                    if (e.type === "mouseenter") {
                        $(this).addClass('btn-default').css('cursor','pointer');
                    } else {
                        $(this).removeClass('btn-default');
                    }
                });
		    });
		}
            }
	});
     }
}

setPopovers("[id$=address_district]");
setPopovers("[id$=address_vdc]");
setPopovers("[id$=-vdc]");
setPopovers("[id$=-district]");
