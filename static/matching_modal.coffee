toggleState = (ele) ->
  ele.toggleClass('btn-default btn-success disabled')


checkForCanon = ->
  form_name = $('#form_name')[0]
  form_age = $('#form_age')[0]
  form_phone = $('#form_phone')[0]
  if form_name.firstElementChild.innerHTML == window.person.name
    toggleState $(form_name.lastElementChild).children()
  if form_age.firstElementChild.innerHTML == window.person.age
    toggleState $(form_age.lastElementChild).children()
  if form_phone.firstElementChild.innerHTML == window.person.phone
    toggleState $(form_phone.lastElementChild).children()

save = (name, phone, age) ->
  console.log name, phone, age
  $.post dutils.urls.resolve('matching_modal', id: window.person.id),
    canonical_name: name
    canonical_phone: phone
    canonical_age: age
  , (data) ->
    console.log data

get_info = (attribute) ->
  $matched = $("##{attribute}s.attribute .matched")
  attrib_val = ''
  $matched.find('li > :first-child').each (idx, ele) ->
    $ele = $(ele)
    if $ele.siblings().children('.btn-success').length > 0
      attrib_val = $ele.data('id')
  obj =
    value: attrib_val || $("#form_#{attribute} > span:first-child").text()
    create: !attrib_val
  console.log obj
  obj

@init = ->

  checkForCanon()

  $buttons = $('.input-group button')
  $buttons.click ->
    $this = $(this)

    $button_to_uncheck = $this.parents('.attribute').find('button.btn-success')

    toggleState $button_to_uncheck
    #$this.toggleClass('btn-default btn-success disabled')

    $text_span = $this.parent().siblings().eq(0)
    $text = $text_span.text()

    $matching_spans = $this.parents('.attribute').find("span:contains(#{$text})")
    $matching_spans = $this.parents('.attribute').find("span").filter ->
      $(this).text() == $text

    toggleState $matching_spans.siblings().children('button')
  $save = $('#save')
  $save.click ->
    save(get_info('name'), get_info('phone_number'), get_info('age'))
  $save_and_use = $('#save_and_use')
  $go_back = $('#go_back')