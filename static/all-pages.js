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
        $('input[type="radio"]').click(calculateTotal);
        calculateTotal();

        setUpValidationPopups();

        var checkboxManagers = {};
        $.each([
            ['victim_caste', 1],
            ['victim_occupation', 1],
            ['victim_marital_status', 1],
            ['victim_lives_with', 1],
            ['victim_is_literate', 1],
            ['victim_primary_guardian', 1],
            ['victim_parents_marital_status', 1],
            ['victim_education_level', 1],
            ['migration_plans', 1],
            ['primary_motivation', 1],
            ['victim_where_going', 1],
            ['manpower_involved', 1],
            ['victim_recruited_in_village', 1],
            ['brokers_relation_to_victim', 1],
            ['victim_how_met_broker', 1],
            ['victim_how_expense_was_paid', 1],
            ['broker_works_in_job_location', 1],
            ['victim_first_time_crossing_border', 1],
            ['victim_primary_means_of_travel', 1],
            ['victim_stayed_somewhere_between', 1],
            ['victim_was_hidden', 1],
            ['victim_was_free_to_go_out', 1],
            ['passport_made', 1],
            ['victim_passport_with_broker', 1],
            ['victim_traveled_with_broker_companion', 1],
            ['companion_with_when_intercepted', 1],
            ['planning_to_meet_companion_later', 1],
            ['money_changed_hands_broker_companion', 1],
            ['meeting_at_border', 1],
            ['victim_knew_details_about_destination', 1],
            ['other_involved_person_in_india', 1],
            ['other_involved_husband_trafficker', 1],
            ['other_involved_someone_met_along_the_way', 1],
            ['other_involved_someone_involved_in_trafficking', 1],
            ['other_involved_place_involved_in_trafficking', 1],
            ['victim_has_worked_in_sex_industry', 1],
            ['victim_place_worked_involved_sending_girls_overseas', 1],
            ['awareness_before_interception', 1],
            ['attitude_towards_tiny_hands', 1],
            ['victim_heard_gospel', 1],
            ['victim_beliefs_now', 1],
            ['guardian_knew_was_travelling_to_india', 1],
            ['family_pressured_victim', 1],
            ['family_will_try_sending_again', 1],
            ['victim_feels_safe_at_home', 1],
            ['victim_wants_to_go_home', 1],
            ['victim_home_had_sexual_abuse', 1],
            ['victim_home_had_physical_abuse', 1],
            ['victim_home_had_emotional_abuse', 1],
            ['victim_guardian_drinks_alcohol', 1],
            ['victim_guardian_uses_drugs', 1],
            ['victim_family_economic_situation', 1],
            ['victim_had_suicidal_thoughts', 1],
            ['legal_action_against_traffickers', 1],
            ['reason_no_legal', 1],
            ['interviewer_recommendation', 1],
            ['other_people_and_places_involved', 1]
        ], function(i, checkboxAttrs) {
            var name = checkboxAttrs[0];
            var maxAllowedChecked = checkboxAttrs[1];
            checkboxManagers[name] = {
                name: name,
                maxAllowedChecked: maxAllowedChecked,
                checkedOrder: $.makeArray($('#'+name+' input[type="checkbox"]:checked'))
            };
        });

        $('input[type="checkbox"]').click(function() {
            var name = $(this).attr('name');
            if (!(name in checkboxManagers)) {
                name = $(this).parents('.checkbox-group-marker').attr('id');
            }
            var manager = checkboxManagers[name];

            if (manager) {
                if ($(this).is(':checked')) {
                    var numberChecked = $('#'+name+' input[type="checkbox"]:checked').length;
                    if (numberChecked > manager.maxAllowedChecked) {
                        var last = manager.checkedOrder.shift();
                        $(last).attr('checked', null);
                    }
                    manager.checkedOrder.push(this);
                }
                else {
                    manager.checkedOrder.splice(
                        manager.checkedOrder.indexOf(this), 1);
                }
            }
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
        step: 30
    });

    var bodyClass = $('body').attr('id');
    if (bodyClass in DREAMSUITE) {
        DREAMSUITE[bodyClass]();
    }
});

