var adjustPopoverPosition = true;
var largestPopoverButtonWidth = null;
var locationType = '';

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
	        container: 'body',
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
        $(element).on('shown.bs.popover', function(){
            $("#district_create_page").click(
                    function(e){
                        e.preventDefault();
                        $("#modal").load(this.href, function(){$("#modal").modal("show");
                    });
            });
        });
	    $(element).blur(function() {
	    	if($('.popover').hasClass('in'))
	    	{
		    	$(this).popover('hide');
                adjustPopoverPosition = true;
			}	
	    });
        var timer = null;
	    $(element).keyup(function(){
            if (timer) {
                $("#loading").css("display", "none");
                clearTimeout(timer);
            }

            if(!$('.popover').hasClass('in'))
            {
                $(this).popover('show');
            }
            input = $(element).val();
            if(element.id.indexOf("district") > 0){
                locationType = "district";
            } else{
                locationType = "vdc";
            }

            if ( input !== "" && input.length >= 2 ) {
                $("#loading").css("display", "block");
                $("#popover-location-info").empty();
                timer = setTimeout(function () {
                    callFuzzyApi(input, locationType, element)
                }, 400);
            }
	    });
	});
}

function callFuzzyApi(input, locationType, element){
    var unorderedList = $("#popover-location-info");

    var requestData = locationType+"="+input;
    if (locationType === "vdc"){
        var district_value = $("#id_interceptees-" + element.id.split('-')[1] + '-district').val();
        if (district_value.length > 0) {
            requestData = requestData + '&district=' + district_value;
        }
    }
    $.ajax({
        url: "/data-entry/geocodelocation/"+locationType+"/",
        data: requestData
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
                $("#loading").css( "display", "none" );
            }
        });
}

setPopovers("[id$=address_district]");
setPopovers("[id$=address_vdc]");
setPopovers("[id$=-vdc]");
setPopovers("[id$=-district]");
