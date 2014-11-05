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

$ ->

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

    toggleState $matching_spans.siblings().children('button')
#  $('.modal').modal()