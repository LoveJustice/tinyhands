$cur_input = ""

setupInputHandlers = ($ui) ->
  $fuzzy_ui_eles = $("[data-fuzzy-ui]")
  # When focusing on input, show it
  $fuzzy_ui_eles.focus ->
    $this = $(this)
    $cur_input = $this
    $ui.css({top: $this.offset().top+$this.outerHeight()+15, left: $this.offset().left})
    search $this.val(), $ui, display_results if $this.val().length > 0
    $ui.find("img").attr("src", "").hide()
    $ui.show()
  # When clicking away, hide
  $(document).click (e) ->
    $target = $(e.target)
    if !$target.attr("data-fuzzy-ui") and e.target.id != 'fuzzymatching-ui' and $target.parents('#fuzzymatching-ui').length == 0
      $ui.hide()

  # Searching
  $fuzzy_ui_eles.keyup (e) ->
    if e.which not in [16, 17, 18, 37, 38, 39, 40]
      search $(this).val(), $ui, display_results

search = (input, $ui, callback) ->
  console.log callback
  if input.length == 0
    return
  $.get $ui.data("ajax"), {name: input}, (data) ->
    if data.success
      results = []
      data.data.forEach (group) ->
        names = group[1]
        scores = group[2]
        id = group[0]
        photo = group[3]
        $.each names, (idx) ->
          results.push {
            id: id,
            name: names[idx],
            score: scores[idx],
            photo: photo
          }
      callback(results, $ui)

display_results = (results, $ui) ->
  $ul = $ui.find("ul")
  $ul.children().remove()
  if results.length > 0
    for item in results.sort((a, b) ->
        return b.score - a.score)
      $span = $("<span>").addClass("name").text(item.name)
      $li = $("<li class='person'>").attr("id", item.id).text("(#{item.score})").data("photo", item.photo).append($span)
      $ul.append($li)
  else
      $li = $("<li>").text("Type to search for matches")
      $ul.append($li)


$ ->
  $modal = $('#matching_modal')
  $ui = $("#fuzzymatching-ui")
  setupInputHandlers($ui)
  # When you click on a name, show the modal
  $ui.on "click", "li.person", ->
    $ui.hide()
    $this = $(this)
    url = dutils.urls.resolve('matching_modal', id: this.id)
    $row = $cur_input.parents('tr')
    name = encodeURIComponent $row.find('#fuzzy_name').val()
    phone = encodeURIComponent $row.find('#fuzzy_phone_contact').val()
    age = encodeURIComponent $row.find('#fuzzy_age').val()
    built_url = "#{url}?name=#{name}&phone=#{phone}&age=#{age}"
    $modal.load built_url, ->
      $modal.modal()
      init()
#    name = $this.children(".name").text()
#    $cur_input.val(name)
#    $button = $cur_input.parent().parent().find(".photo-upload-button")
#    $button.prop("disabled", true)
#    $button.children().css("color", "grey")
  # Hover image
  $ui.on "mouseover", "li.person", ->
    $ui.find("img").attr("src", "#{$(this).data("photo")}").show()
  $popover_button = $("button.show-matches")
  $popover_button.popover
    content: $("#fuzzymatching-ui2").html()
    html: true
    animation: false
    placement: "bottom"
    trigger: "click"
    template: '<div class="popover" role="tooltip" style="width: 300px"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"><ul></ul></div></div>'
  $popover_button.on "shown.bs.popover", ->
    $popover = $(this).siblings(".popover").children(".popover-content")
    search $("[data-fuzzy-ui]").val(), $popover, display_results if $("[data-fuzzy-ui]").val().length > 0
#    $popover.html("<a href=\"#\">hi</a>")
