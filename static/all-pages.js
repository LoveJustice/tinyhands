function setUpPermissionsCheckboxes() {
    $('input[type="checkbox"]').each(function() {
        var $label = $(this).parents('label');
        if ($(this).prop('checked')) {
            $label.addClass('btn-success');
            $label.find('.yesno').text('Yes');
        }
        else {
            $label.addClass('btn-danger');
            $label.find('.yesno').text('No');
        }
    });
    $('input[type="checkbox"]').click(function() {
        var $label = $(this).parents('label');
        if ($(this).parents('label').hasClass('btn-danger')) {
            $label.removeClass('btn-danger').addClass('btn-success');
            $label.find('.yesno').text('Yes');
        }
        else if ($(this).parents('label').hasClass('btn-success')) {
            $label.removeClass('btn-success').addClass('btn-danger');
            $label.find('.yesno').text('No');
        }
    });
}


var DREAMSUITE = {

    account_form: function() {
        setUpPermissionsCheckboxes();
    },
    permissions_matrix: function() {
        setUpPermissionsCheckboxes();
        $('option:contains("---------")').remove();
    },
    access_defaults: function() {
        setUpPermissionsCheckboxes();
        $('#add-another').click(function() {
            var formIdx = $('#id_form-TOTAL_FORMS').val();
            $('#permissions-rows-container').append($('#empty-form').html().replace(/__prefix__/g, formIdx));
            $('#id_form-TOTAL_FORMS').val(parseInt(formIdx) + 1);
            setUpPermissionsCheckboxes();
        });
        $('#permissions-form').submit(function(event) {
            var choice = confirm('Are you sure you want to save changes?');
            if (!choice) {
                event.preventDefault();
            }
        });
        $('.permissions-delete-form').submit(function(event) {
            var choice = confirm('Are you sure you want to delete this permission set?');
            if (!choice) {
                event.preventDefault();
            }
        });
    },
    default: function() {}

};

$(document).ready(function() {
    $('.alert').slideDown();
    setTimeout(function() {
        $('.alert').slideUp();
    }, 4000);

    var bodyClass = $('body').attr('class');
    if (bodyClass in DREAMSUITE) {
        DREAMSUITE[bodyClass]();
    }
});

