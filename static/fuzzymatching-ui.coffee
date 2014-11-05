$cur_input = ""
$ ->
  $modal = $('#matching_modal')
  $ui = $("#fuzzymatching-ui")
  setupInputHandlers($ui)
  # When you click on a name, show the modal
  $ui.on "click", "li.person", ->
    $this = $(this)
    $modal.modal()
#    name = $this.children(".name").text()
#    $cur_input.val(name)
#    $button = $cur_input.parent().parent().find(".photo-upload-button")
#    $button.prop("disabled", true)
#    $button.children().css("color", "grey")
  # Hover image
  $ui.on "mouseover", "li.person", ->
    $ui.find("img").attr("src", "/media/#{$(this).data("photo")}").show()



setupInputHandlers = ($ui) ->
  $fuzzy_ui_eles = $("[data-fuzzy-ui]")
  # When focusing on input, show it
  $fuzzy_ui_eles.focus ->
    $this = $(this)
    $cur_input = $this
    $ui.css({top: $this.offset().top+$this.outerHeight()+15, left: $this.offset().left})
    search $this.val(), $ui if $this.val().length > 0
    $ui.find("img").attr("src", "").hide()
    $ui.show()
  # When clicking away, hide
  $(document).click (e) ->
    $target = $(e.target)
    if !$target.attr("data-fuzzy-ui") and e.target.id != 'fuzzymatching-ui' and $target.parents('#fuzzymatching-ui').length == 0
      $ui.hide()

  # Searching
  $fuzzy_ui_eles.keyup (e) ->
    if e.which not in [16, 17, 37, 38, 39, 40]
      console.log "searching"
      search $(this).val(), $ui

search = (input, $ui) ->
  console.log $ui.data("ajax"), {name: input}
  $.get $ui.data("ajax"), {name: input}, (data) ->
    if data.success
      results = []
      data.data.forEach (item) ->
        console.log item
        obj = JSON.parse(item[2])[0]
        results.push({id: obj.id, name: item[0], score: item[1], photo: obj.photo})
      display_results(results, $ui)

display_results = (results, $ui) ->
  $ul = $ui.find("ul")
  $ul.children().remove()
  if results.length > 0
    for item in results.slice(0, 6)
      $span = $("<span>").addClass("name").text(item.name)
      $li = $("<li class='person'>").attr("id", item.id).text("(#{item.score})").data("photo", item.photo).append($span)
      $ul.append($li)
  else
      $li = $("<li>").text("Type to search for matches")
      $ul.append($li)
