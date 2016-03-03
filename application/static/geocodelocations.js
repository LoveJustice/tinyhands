var adjustPopoverPosition = true;
var largestPopoverButtonWidth = null;
var locationType = '';

function setPopovers(id)
{
	$(id).each(function(index, element) {
        if($(element).attr('id').indexOf("-address2") != -1 || $(element).attr('id').indexOf("address2") != -1){
            nameOfForm = "#geocode-address2-form";
        }
        else{
            nameOfForm = "#geocode-address1-form";
        }
	    $(element).popover({
	        content: $(nameOfForm).html(),
	        html:true,
	        placement:'bottom',
	        container: 'body',
            trigger: 'focus'
	    });
        $(element).on('shown.bs.popover', function(){
            $("#address2_create_page").click(
                    function(e){
                        e.preventDefault();
                        $("#modal").load(this.href, function(){$("#modal").modal("show");
                    });
            });
        });
        $(element).on('shown.bs.popover', function(){
            $("#address1_create_page").click(
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
            if(element.id.indexOf("address1") > 0){
                locationType = "address1";
            }
            else{
                locationType = "address2";
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
    if (locationType === "address2"){
        var address1_value = find_address1_value(element);
        if (address1_value.length > 0) {
            requestData = requestData + '&address1=' + address1_value;
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

function find_address1_value(element) {
    var address1_value = "";
    if (element.id === "id_victim_address2")
    {
       address1_value = $("#id_victim_address1").val();
    }
    else if (element.id === "id_victim_guardian_address2")
    {
       address1_value = $("#id_victim_guardian_address1").val();
    }
    else if (element.id.indexOf("id_person_boxes-") > -1 && element.id.indexOf("address2") > -1)
    {
       address1_value = $("#id_person_boxes-" + element.id.split('-')[1] + '-address1').val();
    }
    else if (element.id.indexOf("id_location_boxes-") > -1 && element.id.indexOf("address2") > -1)
    {
       address1_value = $("#id_location_boxes-" + element.id.split('-')[1] + '-address1').val();
    }
    else
    {
       address1_value = $("#id_interceptees-" + element.id.split('-')[1] + '-address1').val();
    }
    return address1_value;
}

setPopovers("[id$=address1]");
setPopovers("[id$=address2]");
setPopovers("[id$=-address2]");
setPopovers("[id$=-address1]");
