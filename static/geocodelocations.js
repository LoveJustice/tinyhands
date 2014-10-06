function setPopovers(id)
{
	$(id).each(function(index, element) {
	    $(element).popover({
	        content: $("#geocode-form").html(),
	        html:true,
	        placement:'bottom',
	        container: 'body',
	    });
	    $(element).bind('keyup',function (){
	    	if(!$('.popover').hasClass('in'))
	    	{
				$(this).popover('show');
			}
	    });
	    $(element).blur(function() {
	    	if($('.popover').hasClass('in'))
	    	{
		    	$(this).popover('hide');
			}	
	    });
	});
}
setPopovers("[id$=-vdc]");
setPopovers("[id$=-district]");