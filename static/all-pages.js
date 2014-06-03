function setUpValidationPopup(elem, kind) {
    var id = $(elem).data('id');
    if (id == 'ignore_warnings') {
        return;
    }
    var message = $(elem).data('message');

    if (kind === 'error') {
        message = 'Error: ' + message;
    }
    if (kind === 'warning') {
        message = 'Warning: ' + message;
    }

    var $elem = $('#id_' + id);
    if ($elem.length === 0) {
        $elem = $('[name="'+id+'"]').eq(0);
    }

    $elem.attr('data-toggle', 'tooltip').attr('title', message);


    var opts = { trigger: 'manual' };
    if (!$elem.is('[data-placement]')) {
        opts.placement = 'top';
    }
    else {
        opts.placement = $.trim($elem.data('placement'));
        $elem.attr('data-placement', '');
    }

    $elem.tooltip(opts).tooltip('show');
}


function setUpValidationPopups() {
    $('.error-for-popup').each(function() {
        console.log(this);
        setUpValidationPopup(this, 'error');
    });
    $('.warning-for-popup').each(function() {
        console.log(this);
        setUpValidationPopup(this, 'warning');
    });

    $('.tooltip-inner').each(function() {
        var kind = $(this).text().split(':')[0].toLowerCase();
        $(this).addClass('kind-' + kind);
    });
}

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

    account_create: function() {
        this.account_update();
    },
    account_update: function() {
        setUpPermissionsCheckboxes();
        $('select').change(function() {
            for (var i=0; i<window.defaultPermissionSets.length; i++) {
                var set = window.defaultPermissionSets[i];
                if (set.id === parseInt($(this).val())) {
                    for (var key in set) {
                        var toBe = set[key];
                        var $checkbox = $('#id_' + key);
                        var current = !!$checkbox.prop('checked');
                        if (toBe !== current) {
                            $checkbox.trigger('click');
                        }
                    }
                }
            }
        });
    },

    access_control: function() {
        setUpPermissionsCheckboxes();
        $('option:contains("---------")').remove();
        $('select').change(function() {
            var rowIdx = parseInt($(this).parents('td').find('input').val()) - 1;
            for (var i=0; i<window.defaultPermissionSets.length; i++) {
                var set = window.defaultPermissionSets[i];
                if (set.id === parseInt($(this).val())) {
                    for (var key in set) {
                        var toBe = set[key];
                        var $checkbox = $('#id_form-' + rowIdx + '-' + key);
                        var current = !!$checkbox.prop('checked');
                        if (toBe !== current) {
                            $checkbox.trigger('click');
                        }
                    }
                }
            }
        });
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

        $('.in-use-button').tooltip();
    },

    interceptionrecord_create: function() {
        this.interceptionrecord_update();
    },

    interceptionrecord_update: function() {
        function calculateTotal() {
            var total = 0;
            $('input[type="checkbox"]').each(function(id, elem) {
                var value = $.trim($(elem).next('.red-flag').text());
                if (value !== '') {
                    if ($(elem).prop('checked')) {
                        total += parseInt(value);
                    }
                }
            });
            $('#calculated-total').text(total);
        }
        $(document).ready(function() {
            $('input[type="checkbox"]').click(calculateTotal);
            calculateTotal();
            var resize = function() {
                $('.photo').each(function() {
                    var width = $(this).width();
                    $(this).height(width);
                    $(this).css('line-height', width + 'px');
                });
            };
            $(window).resize(resize);
            resize();

            setUpValidationPopups();
        });

        // A hack but it works
        if ($('#error-box p').length === 0) {
            $('#error-box').remove();
        }
    },

    victiminterview_create: function() {
        this.victiminterview_update();
    },
    victiminterview_update: function() {
        function calculateTotal() {
            var total = 0;
            $('.alarm-box').each(function(id, elem) {
                var $radio = $(elem).parents('.alarm-box-container').find('input');
                if ($radio.is(':checked')) {
                    total += parseInt($(elem).text());
                }
            });
            $('#calculated-total').text(total);
        }
        $(document).ready(function() {
            $('input[type="radio"]').click(calculateTotal);
            calculateTotal();

            setUpValidationPopups();
        });
    },

    default: function() {}

};

$(document).ready(function() {
    $('.alert').slideDown();
    setTimeout(function() {
        $('.alert').not('.no-remove').slideUp();
    }, 4000);

    $('input[id*=date]').datetimepicker({
        format:'m/d/Y H:i',
        hours12: true,
        step: 15
    });

    var bodyClass = $('body').attr('id');
    if (bodyClass in DREAMSUITE) {
        DREAMSUITE[bodyClass]();
    }
});

