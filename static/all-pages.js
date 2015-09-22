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
  $(className).parents('label').click(function() {
    //alert("In function");
    var $label = $(this);
    var $input = $label.find('input');
    if ($label.hasClass('btn-danger')) {
      //alert("here1");
      $input.attr('checked','checked');
      $label.removeClass('btn-danger').addClass('btn-success');
      $label.find(className).text(checkedText);
    }
    else if ($label.hasClass('btn-success')) {
      //alert("here2");
      $input.removeAttr('checked');
      $label.removeClass('btn-success').addClass('btn-danger');
      $label.find(className).text(uncheckedText);
    }
    event.stopPropagation();
    event.preventDefault();
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
  //  var name = $(elem).attr('id');
  //  var maxAllowedChecked = $(elem).data('max') || 1;
  //  checkboxManagers[name] = {
  //    name: name,
  //    maxAllowedChecked: maxAllowedChecked,
  //    checkedOrder: $.makeArray($('#'+name+' input[type="checkbox"]:checked'))
  //  };
  //});

  //$('input[type="checkbox"]').click(function() {
  //  var name = $(this).attr('name');
  //  if (!(name in checkboxManagers)) {
  //    name = $(this).parents('.checkbox-group-marker').attr('id');
  //  }
  //  var manager = checkboxManagers[name];

  //  if (manager) {
  //    if ($(this).is(':checked')) {
  //      var numberChecked = $('#'+name+' input[type="checkbox"]:checked').length;
  //      if (numberChecked === 0) {
  //        manager.checkedOrder = [];
  //      }
  //      else if (numberChecked > manager.maxAllowedChecked) {
  //        var last = manager.checkedOrder.shift();
  //        $(last).attr('checked', null);
  //      }
  //      manager.checkedOrder.push(this);
  //    }
  //    else {
  //      manager.checkedOrder.splice(
  //        manager.checkedOrder.indexOf(this), 1);
  //    }
  //  }
  //});

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
    //$('#id_contact_noticed').click(function() {
    //  $('#id_staff_noticed').attr('checked', null);
    //  $('input[id*="id_noticed_"]').attr('checked', null);
    //});
    //$('#id_staff_noticed').click(function() {
    //  $('#id_contact_noticed').attr('checked', null);
    //  $('input[id*="id_which_contact_"]').attr('checked', null);
    //  $('#contact_paid').find('input[type="checkbox"]').attr('checked', null);
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
    //  var href = $(this).find('a').attr('href');
    //  var id = $(this).find('input').attr('name').split('-')[1];
    //  $('#photo-' + id).append(

    //});
    makeDateTimePickers('#id_date_time_of_interception');

    //$('#save-for-later').click(function() {
    //  var formData = $('form').serialize();

    //});
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
