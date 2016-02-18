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

function photoSelect() {
    $('.photo-manip-controls').click();
    console.log("Test...1.2.3");
}

function makeCheckboxAppearAsAButton(className,checkedText,uncheckedText) {
    $(className).parents('label').each(function() {
        var $label = $(this);
        var $input = $label.find('input');
        $input.hide();
        if ($input.prop('checked')) {
            $label.addClass('btn-success');
            $label.find(className).text(checkedText);
        }
        else {
            $label.addClass('btn-danger');
            $label.find(className).text(uncheckedText);
        }
    });
    $(className).parents('label').unbind('click').click(function(event) {
        var $label = $(this);
        var $input = $label.find('input');
        if ($label.hasClass('btn-danger')) {
            $input.prop('checked', true);
            $label.removeClass('btn-danger').addClass('btn-success');
            $label.find(className).text(checkedText);
        }
        else if ($label.hasClass('btn-success')) {
            $input.prop('checked', false);
            $label.removeClass('btn-success').addClass('btn-danger');
            $label.find(className).text(uncheckedText);
        }
        event.stopPropagation();
        event.preventDefault();
    });
}

function setUpLimitedChoicesCheckboxGroups() {

    // This simpler version just limits it to one checkbox since thats all we have right now
    $('input[type="checkbox"]').click(function() {
        var $selectedBox = $(this);
        var $container = $selectedBox.parents('.checkbox-group-marker').eq(0);
        if ($selectedBox.parent().hasClass('multiple-checkboxes-allowed')){
            $container.find('input[type="checkbox"]').each(function () {
                var $currentBox = $(this);
                if($currentBox.parent().hasClass('single-checkbox-allowed')) {
                    $currentBox.attr('checked', null);
                }
            });
            return;
        }
        else if ($selectedBox.parent().hasClass('single-checkbox-allowed')) {
            $container.find('input[type="checkbox"]').not(this).attr('checked', null);
            return;
        }
        else if ($container.length === 0) {
            return;
        }
        $container.find('input[type="checkbox"]').not(this).attr('checked', null);
    });
}

function setUpResumeIncompleteFormSystem(which) {
    var storedForms = JSON.parse(localStorage.getItem('saved-'+which+'s') || '{}');
    for (var formNumber in storedForms) {
        var formData = storedForms[formNumber];
        $('#saved-for-later-list').append(
            $('<option value="'+formData+'">'+formNumber+'</option>')
        );
    }

    $('#saved-for-later-list').change(function() {
        var allInputs = document.getElementsByTagName("input");
        for (var i = 0, max = allInputs.length; i < max; i++){
            if (allInputs[i].type === 'checkbox')
            allInputs[i].checked = false;
            else if (allInputs[i].type == 'text')
            allInputs[i].value = '';
            else if (allInputs[i].type == 'number')
            allInputs[i].value = '';
        }
        var allSelects = document.getElementsByTagName("select");
        for (var i = 0, max = allSelects.length; i <max; i++){
            if (allSelects[i].id != "saved-for-later-list"){
                allSelects[i].selectedIndex = 0;
                console.log(allSelects[i].id);
            }
        }

        $('form').deserialize($(this).val());
    });


    $('#save-for-later').click(function() {
        var formNumber = $('#id_'+which+'_number').val();
        if (!formNumber) {
            alert('Please enter a '+which.toUpperCase()+' # to save this form for later.');
            return;
        }
        var storedForms = JSON.parse(localStorage.getItem('saved-'+which+'s') || '{}');
        storedForms[formNumber] = $('form').serialize();
        localStorage.setItem('saved-'+which+'s', JSON.stringify(storedForms));

        alert('This form has been saved for later.  Come back to the ' + which.toUpperCase() +
        ' create page and select the ' + which.toUpperCase() +
        ' number from the top dropdown to resume entering data.');
        window.location.href = '/data-entry/'+which+'s/';
    });
}

function clearCompletedForms(which) {
    var storedForms = JSON.parse(localStorage.getItem('saved-'+which+'s') || '{}');
    $('.'+which+'-number').each(function() {
        var num = $(this).text();
        if (num in storedForms) {
            delete storedForms[num];
        }
    });
    localStorage.setItem('saved-'+which+'s', JSON.stringify(storedForms));
}

var DREAMSUITE = {

    borderstations_update: function() {
        makeCheckboxAppearAsAButton('.openclosed','Station Status: Open','Station Status: Closed');
    },

    account_create: function() {
        this.account_update();
    },

    account_update: function() {
        makeCheckboxAppearAsAButton('.yesno','Yes','No');
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
        makeCheckboxAppearAsAButton('.yesno','Yes','No');
        $('option:contains("---------")').remove();
        $('select').change(function() {
            var userId = parseInt($(this).parents('td').find('input').val());
            var rowId = $('input[value=' + userId + ']')[0].id.slice(0,-3);
            for (var i=0; i<window.defaultPermissionSets.length; i++) {
                var set = window.defaultPermissionSets[i];
                if (set.id === parseInt($(this).val())) {
                    for (var key in set) {
                        if(key == 'name' || key == 'id') {
                            continue;
                        }
                        var toBe = set[key];
                        var $checkbox = $('#' + rowId + '-' + key);
                        var current = !!$checkbox.prop('checked');
                        if (toBe !== current) {
                            $checkbox.parents('label')[0].click();
                        }
                    }
                }
            }
        });
    },

    access_defaults: function() {
        makeCheckboxAppearAsAButton('.yesno','Yes','No');
        $('#add-another').click(function() {
            var formIdx = $('#id_form-TOTAL_FORMS').val();
            $('#permissions-rows-container').append($('#empty-form').html().replace(/__prefix__/g, formIdx));
            $('#id_form-TOTAL_FORMS').val(parseInt(formIdx) + 1);
            makeCheckboxAppearAsAButton('.yesno','Yes','No');
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

    budget_create_api: function(){
        $(function() {
            var queryDate = '2009-11-01',
            dateParts = queryDate.match(/(\d+)/g)
            realDate = new Date(dateParts[0], dateParts[1] - 1, dateParts[2]);
            // months are 0-based!

            $('#startDate').datepicker({
                dateFormat: "MM yy"
            }) // format to show
            .datepicker('setDate', realDate)
            .datepicker("option", "changeMonth", true)
            .datepicker("option", "changeYear", true)
            .datepicker("option", "showButtonPanel", true)
            .datepicker("option", "onClose", function(e){
                var month = $("#ui-datepicker-div .ui-datepicker-month :selected").val();
                var year = $("#ui-datepicker-div .ui-datepicker-year :selected").val();
                $(this).datepicker("setDate",new Date(year,month,1));
            })
        });
    },

    budget_update_api: function(){
        $(function() {
            var queryDate = '2009-11-01',
            dateParts = queryDate.match(/(\d+)/g)
            realDate = new Date(dateParts[0], dateParts[1] - 1, dateParts[2]);
            // months are 0-based!

            $('#startDate').datepicker({
                dateFormat: "MM yy"
            }) // format to show
            .datepicker('setDate', realDate)
            .datepicker("option", "changeMonth", true)
            .datepicker("option", "changeYear", true)
            .datepicker("option", "showButtonPanel", true)
            .datepicker("option", "onClose", function(e){
                var month = $("#ui-datepicker-div .ui-datepicker-month :selected").val();
                var year = $("#ui-datepicker-div .ui-datepicker-year :selected").val();
                $(this).datepicker("setDate",new Date(year,month,1));
            })
        });
    },

    /********************** IRF **********************/
    interceptionrecord_list: function() {
        clearCompletedForms('irf');
    },

    interceptionrecord_create: function() {
        this.interceptionrecord_update();

        setUpResumeIncompleteFormSystem('irf');
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

        // A hack but it work
        if ($('#error-box p').length === 0) {
            $('#error-box').remove();
        }

        $('.photo-upload-button').click(function() {
            $(this).parents('td').find('input').click();

        });
        $('.photo-upload-button').parents('td').find('input[type="file"]').change(function(event) {
            $(this).parents('td').find('button').addClass('btn-success', 'btn-inverse').attr('title', $(this).val());
        });

        makeDateTimePickers('#id_date_time_of_interception');

    },

    interceptionrecord_detail: function() {
        this.interceptionrecord_update();

        var $form = $('#interception-record-form');
        $form.find('input, button, select, textarea').attr('disabled', 'disabled');
        $('#footer').hide();
    },

    /********************** VIF **********************/
    victiminterview_list: function() {
        clearCompletedForms('vif');
    },

    victiminterview_create: function() {
        this.victiminterview_update();

        setUpResumeIncompleteFormSystem('vif');
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

        if ($('#error-box p').length === 0) {
            $('#error-box').remove();
        }

        setUpValidationPopups();

        setUpLimitedChoicesCheckboxGroups();

        $('#id_victim_where_going_india_other_value').keyup(function(event) {
            $("#id_victim_where_going_india_other").prop('checked', $(this).val() != "");
            $("#id_victim_where_going_region_india").prop('checked', true);
            $("#id_victim_where_going_region_gulf").prop('checked', false);
            $("#id_victim_where_going_gulf_other").prop('checked', false);
            $("#id_victim_where_going_gulf_other_value").val("");
        });

        $('#id_victim_where_going_gulf_other_value').keyup(function(event) {
            $("#id_victim_where_going_gulf_other").prop('checked', $(this).val() != "");
            $("#id_victim_where_going_region_gulf").prop('checked', true);
            $("#id_victim_where_going_region_india").prop('checked', false);
            $("#id_victim_where_going_india_other").prop('checked', false);
            $("#id_victim_where_going_india_other_value").val("");
        });

        $("#id_victim_where_going_india_other").click(function() {
            if(!$(this).prop('checked')){
                $('#id_victim_where_going_india_other_value').val("");
            } else {
                $('#id_victim_where_going_gulf_other_value').val("");
            }
        });

        $("#id_victim_where_going_gulf_other").click(function() {
            if(!$(this).prop('checked')){
                $('#id_victim_where_going_gulf_other_value').val("");
            } else {
                $('#id_victim_where_going_india_other_value').val("");
            }
        });

        $('#id_victim_where_going_region_india').click(function() {
            if ($('#id_victim_where_going_region_india').prop('checked') == false) {
                $('input[id*="id_victim_where_going_india_"]').prop('checked', false);
            }
            $('#id_victim_where_going_region_gulf').prop('checked', false);
            $('input[id*="id_victim_where_going_gulf_"]').prop('checked', false);
        });
        $('#id_victim_where_going_region_gulf').click(function() {
            if ($('#id_victim_where_going_region_gulf').prop('checked') == false) {
                $('input[id*="id_victim_where_going_gulf_"]').prop('checked', false);
            }
            $('#id_victim_where_going_region_india').prop('checked', false);
            $('input[id*="id_victim_where_going_india_"]').prop('checked', false);
        });

        $('#victim_where_going_gulf').find('input[type="checkbox"]').click(function() {
            if ( $(this).prop("checked") == true) {
                $('#id_victim_where_going_region_gulf').prop('checked', true);
                $('#id_victim_where_going_region_india').prop('checked', false);
                $('input[id*="id_victim_where_going_india_"]').prop('checked', false);
            }
            else{
                $('#id_victim_where_going_region_gulf').prop('checked', false);
                $('#id_victim_where_going_region_india').prop('checked', false);
                $('input[id*="id_victim_where_going_india_"]').prop('checked', false);
            }
        });
        $('#victim_where_going_india').find('input[type="checkbox"]').click(function() {
            if ( $(this).prop("checked") == true) {
                $('#id_victim_where_going_region_india').prop('checked', true);
                $('#id_victim_where_going_region_gulf').prop('checked', false);
                $('input[id*="id_victim_where_going_gulf_"]').prop('checked', false);
            }
            else{
                $('#id_victim_where_going_region_india').prop('checked', false);
                $('#id_victim_where_going_region_gulf').prop('checked', false);
                $('input[id*="id_victim_where_going_gulf_"]').prop('checked', false);
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

    default: function() {}

};

function reloadPhotos() {
    var photoString = "";
    var pathString = "";
    $('.btn-success.photo-upload-button').each(function(){
        console.log(this.parentNode.parentNode.childNodes[1].childNodes[3].name);
        photoString = photoString + "/" + this.parentNode.parentNode.childNodes[1].childNodes[3].name;
        pathString = pathString + "/" + this.title;
        //localStorage.setItem("item", "TestString");
    });
    localStorage.setItem("pathList", pathString);
    localStorage.setItem("photoList", photoString);
}

$(document).ready(function() {
    $('.alert').slideDown();
    setTimeout(function() {
        $('.alert').not('.no-remove').slideUp();
    }, 4000);

    var bodyClass = $('body').attr('id');
    if (bodyClass in DREAMSUITE) {
        DREAMSUITE[bodyClass]();
    }

    // Semi-colon delimiting the staff name data
    $("ul#dropdown-staff").each(function() {
        $(this).change(function() {
            var line = "";
            $("ul.dropdown-menu:not(#dropdown-staff-who-noticed) input[type=checkbox]").each(function() {
                if($(this).is(":checked")) {
                    line += $("+ span", this).text() + ",";
                }
            });
            $("input#id_staff_name").val(line);
            $("input#id_interviewer").val(line);

        });
    });

    $("ul#dropdown-staff-who-noticed").each(function() {
        $(this).change(function() {
            var line = "";
            $("ul#dropdown-staff-who-noticed input[type=checkbox]").each(function() {
                if($(this).is(":checked")) {
                    line += $("+ span", this).text() + ",";
                }
            });
            $("input#id_staff_who_noticed").val(line);

        });
    });
});


// Allows multiple clicks on dropdown instead of automatically closing
$(document).on('click', '.dropdown-menu.dropdown-menu-form', function(e) {
    e.stopPropagation();
});
