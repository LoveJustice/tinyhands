var adjustPopoverPosition = true;
var largestPopoverButtonWidth = null;

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
                adjustPopoverPosition = true;
			}	
	    });
	    $(element).keyup(function(){
            if(!$('.popover').hasClass('in'))
            {
                $(this).popover('show');
            }

            input = $(element).val();
            if(element.id.indexOf("district") > 0){
                callFuzzyApi(input, "district", element);
            } else{
                callFuzzyApi(input, "vdc", element);
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
                if (data.id != -1) {
                    for (i in data) {
                        //Add event for these divs that will extract the text from the div
                        unorderedList.append($('<div class="btn fuzzymatches"></div><br/>').append(data[i].name));
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
                    var inputOffset = $(element).offset().left + (parseFloat($(element).css('width'))/2);
                    var popoverOffset = $('.popover').offset().left + (parseFloat($('.popover').css('width'))/2);
                    var offsetDiff = inputOffset - popoverOffset;
                    var popoverLeft = $('.popover').offset().left + offsetDiff;
                    $('.popover').css('left',popoverLeft+'px');
                }
        });
    }
}

setPopovers("[id$=address_district]");
setPopovers("[id$=address_vdc]");
setPopovers("[id$=-vdc]");
setPopovers("[id$=-district]");
