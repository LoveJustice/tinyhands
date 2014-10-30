$ ->
  $buttons = $('.input-group button')
  $buttons.click ->
    console.log 'click check'
    $this = $(this)

    $button_to_uncheck = $this.parents('.attribute').find('button.btn-success')

    $button_to_uncheck.toggleClass('btn-default btn-success disabled')
    #$this.toggleClass('btn-default btn-success disabled')

    $text_span = $this.parent().siblings().eq(0)
    $text = $text_span.text()

    $matching_spans = $this.parents('.attribute').find("span:contains(#{$text})")

    $matching_spans.siblings().children('button').toggleClass('btn-default btn-success disabled')