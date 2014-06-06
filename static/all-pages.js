function makeDateTimePickers(selector) {
    $(selector).datetimepicker({
        format:'m/d/Y H:i',
        step: 30
    });
}
function makeDatePickers(selector) {
    $(selector).datetimepicker({
        format:'m/d/Y',
        timepicker: false
    });
}

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
        if ($elem.length === 0) {
            $elem = $('#' + id).eq(0);
        }
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
        setUpValidationPopup(this, 'error');
    });
    $('.warning-for-popup').each(function() {
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
function setUpLimitedChoicesCheckboxGroups() {
    // Well, this was supposed to be used to allow restricting
    // a group of checkboxes to a certain number of checks, but
    // now every group only requires one. heh heh heh

    // To add a new checkbox group, add the class checkbox-group-marker and an id that contains the common starting string of each checkbox field.  For example, if you had talked_to_brother,  talked_to_sister, and talked_to_aunt in a group, putting in an id of "talked_to" would make that a group
    //
    // This commented out block almost works but breaks if something clears checkboxes other than this manager
    //var checkboxManagers = {};
    //$('.checkbox-group-marker').each(function(i, elem) {
    //    var name = $(elem).attr('id');
    //    var maxAllowedChecked = $(elem).data('max') || 1;
    //    checkboxManagers[name] = {
    //        name: name,
    //        maxAllowedChecked: maxAllowedChecked,
    //        checkedOrder: $.makeArray($('#'+name+' input[type="checkbox"]:checked'))
    //    };
    //});

    //$('input[type="checkbox"]').click(function() {
    //    var name = $(this).attr('name');
    //    if (!(name in checkboxManagers)) {
    //        name = $(this).parents('.checkbox-group-marker').attr('id');
    //    }
    //    var manager = checkboxManagers[name];

    //    if (manager) {
    //        if ($(this).is(':checked')) {
    //            var numberChecked = $('#'+name+' input[type="checkbox"]:checked').length;
    //            if (numberChecked === 0) {
    //                manager.checkedOrder = [];
    //            }
    //            else if (numberChecked > manager.maxAllowedChecked) {
    //                var last = manager.checkedOrder.shift();
    //                $(last).attr('checked', null);
    //            }
    //            manager.checkedOrder.push(this);
    //        }
    //        else {
    //            manager.checkedOrder.splice(
    //                manager.checkedOrder.indexOf(this), 1);
    //        }
    //    }
    //});

    // This simpler version just limits it to one checkbox since thats all we have right now
    $('input[type="checkbox"]').click(function() {
        var $container = $(this).parents('.checkbox-group-marker').eq(0);
        if ($container.length === 0) {
            return;
        }
        $container.find('input[type="checkbox"]').not(this).attr('checked', null);
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

        setUpLimitedChoicesCheckboxGroups();
        //$('#id_contact_noticed').click(function() {
        //    $('#id_staff_noticed').attr('checked', null);
        //    $('input[id*="id_noticed_"]').attr('checked', null);
        //});
        //$('#id_staff_noticed').click(function() {
        //    $('#id_contact_noticed').attr('checked', null);
        //    $('input[id*="id_which_contact_"]').attr('checked', null);
        //    $('#contact_paid').find('input[type="checkbox"]').attr('checked', null);
        //});

        // A hack but it works
        if ($('#error-box p').length === 0) {
            $('#error-box').remove();
        }

        $('.photo-upload-button').click(function() {
            $(this).parents('td').find('input').click();
            
        });
        $('.photo-upload-button').parents('td').find('input[type="file"]').change(function(event) {
            $(this).parents('td').find('button').addClass('btn-success', 'btn-inverse').attr('title', $(this).val());
        });
        //$('.photo-manip-controls').each(function() {
        //    var href = $(this).find('a').attr('href');
        //    var id = $(this).find('input').attr('name').split('-')[1];
        //    $('#photo-' + id).append(

        //});
        makeDateTimePickers('#id_date_time_of_interception');
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
        $('input[type="checkbox"]').click(calculateTotal);
        calculateTotal();

        setUpValidationPopups();

        setUpLimitedChoicesCheckboxGroups();

        $('#id_victim_where_going_region_india').click(function() {
            $('#id_victim_where_going_region_gulf').attr('checked', null);
            $('input[id*="id_victim_where_going_gulf_"]').attr('checked', null);
        });
        $('#id_victim_where_going_region_gulf').click(function() {
            $('#id_victim_where_going_region_india').attr('checked', null);
            $('input[id*="id_victim_where_going_india_"]').attr('checked', null);
        });
        $('#victim_where_going_gulf').find('input[type="checkbox"]').click(function() {
            $('#id_victim_where_going_region_gulf').attr('checked', 'checked');
            $('#id_victim_where_going_region_india').attr('checked', null);
            $('input[id*="id_victim_where_going_india_"]').attr('checked', null);
        });
        $('#victim_where_going_india').find('input[type="checkbox"]').click(function() {
            $('#id_victim_where_going_region_india').attr('checked', 'checked');
            $('#id_victim_where_going_region_gulf').attr('checked', null);
            $('input[id*="id_victim_where_going_gulf_"]').attr('checked', null);
        });


        // Allow user to hover over the numbers in parens next to some fields to 
        // learn that that is how many may be checked.
        $('.max-allowed').each(function(i, elem) {
            var text = $(elem).text();
            var count = text.substring(1, text.length - 1);
            $(elem).attr(
                'title',
                'At most ' + count + ' may be checked.'
            );
        });

        makeDatePickers('#id_date, #id_victim_how_long_stayed_between_start_date');

        var pagesNeeded = parseInt($('.pages-needed').data('pages-needed'));
        for (var i=1; i<=4; i++) {
            if (i > pagesNeeded) {
                $('.box-page.page-' + i).hide();
                $('.box-page.page-' + i).addClass('hidden');
            }
        }
        $('.add-another-sheet').click(function(event) {
            event.preventDefault();
            var $nextPage = $('.box-page.hidden').eq(0);
            $nextPage.removeClass('hidden');
            $nextPage.slideDown();
        });
    },

    victiminterview_detail: function() {
        this.victiminterview_update();

        var $form = $('#victim-interview-form');
        $form.find('input, button, select, textarea').attr('disabled', 'disabled');
        $('#footer').hide();
    },
    interceptionrecord_detail: function() {
        this.interceptionrecord_update();

        var $form = $('#interception-record-form');
        $form.find('input, button, select, textarea').attr('disabled', 'disabled');
        $('#footer').hide();
    },

    default: function() {}

};

$(document).ready(function() {
    $('.alert').slideDown();
    setTimeout(function() {
        $('.alert').not('.no-remove').slideUp();
    }, 4000);

    var bodyClass = $('body').attr('id');
    if (bodyClass in DREAMSUITE) {
        DREAMSUITE[bodyClass]();
    }
});

