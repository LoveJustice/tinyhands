var adjustPopoverPosition = true;
var largestPopoverButtonWidth = null;

function setPopovers(id)
{
	$(id).each(function(index, element) {
        if($(element).attr('id').indexOf("-vdc") != -1 || $(element).attr('id').indexOf("address_vdc") != -1){
            nameOfForm = "#geocode-vdc-form";
        }
        else{
            nameOfForm = "#geocode-district-form";
        }
	    $(element).popover({
	        content: $(nameOfForm).html(),
	        html:true,
	        placement:'bottom',
            trigger: 'focus'
	    });
        $(element).on('shown.bs.popover', function(){
            $("#vdc_create_page").click(
                    function(e){
                        e.preventDefault();
                        $("#modal").load(this.href, function(){$("#modal").modal("show");
                    });
            });
        });
	    $(element).blur(function() {
            return;
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
            // This is better :)
            callFuzzyApi(input, element.id.indexOf("district") > 0 ? "district" : "vdc", element);
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
                    // This was bad. Still is. You were just getting all popovers on page. NOT good. You aren't the ONLY popover.
                    var inputOffset = $(element).offset().left + (parseFloat($(element).css('width'))/2);
                    var $popover = unorderedList.parents('.popover');
                    var popoverOffset = $popover.offset().left + (parseFloat($popover.css('width'))/2);
                    var offsetDiff = inputOffset - popoverOffset;
                    var popoverLeft = $popover.offset().left + offsetDiff;
                    $popover.css('left',popoverLeft-(parseFloat($(element).css('width'))/2)+'px');
                }
        });
    }
}

setPopovers("[id$=address_district]");
setPopovers("[id$=address_vdc]");
setPopovers("[id$=-vdc]");
setPopovers("[id$=-district]");
