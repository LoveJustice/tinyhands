$cur_input = ""
list_of_names = [
  "Justin Northworth"
  "Justin North"
  "Justice Northwood"
  "Justyn Northwerth"
  "Dustin Waldo"
  "Dustin Waldron"
  "Dusty Waldy"
  "Dustin Waldro"
]
list_of_pics = [
  "/media/interceptee_photos/doge.png"
  "/media/interceptee_photos/doge.png"
  "/media/interceptee_photos/doge.png"
  "/media/interceptee_photos/doge.png"
  "/media/interceptee_photos/38503_1144682394791_1729508_n.jpg"
  "/media/interceptee_photos/38503_1144682394791_1729508_n.jpg"
  "/media/interceptee_photos/38503_1144682394791_1729508_n.jpg"
  "/media/interceptee_photos/38503_1144682394791_1729508_n.jpg"
]
$ ->
  $ui = $("#fuzzymatching-ui")
  setupInputHandlers($ui)
  $items = $ui.find('li')
  # When you click on a name, insert it
  $ui.on "click", "li", ->
    $this = $(this)
    name = $this.children(".name").text()
    console.log name
    $cur_input.val(name)
    $button = $cur_input.parent().parent().find(".photo-upload-button")
    $button.prop("disabled", true)
    $button.children().css("color", "grey")
  # Hover image
  $ui.on "mouseover", "li", ->
    $ui.find("img").attr("src", list_of_pics[this.id])



setupInputHandlers = ($ui) ->
  $fuzzy_ui_eles = $("[data-fuzzy-ui]")
  # When focusing on input, show it
  $fuzzy_ui_eles.focus ->
    $this = $(this)
    $cur_input = $this
    $ui.css({top: $this.offset().top+$this.outerHeight()+15, left: $this.offset().left})
    search $this.val(), $ui
    $ui.find("img").attr("src", "")
    $ui.show()
  # When clicking away, hide
  $(document).click (e) ->
    if !$(e.target).attr("data-fuzzy-ui")
      $ui.hide()

  # Searching
  $fuzzy_ui_eles.keyup (e) ->
    if e.which not in [16, 17, 37, 38, 39, 40]
      search $(this).val(), $ui

search = (input, $ui) ->
  $.get $ui.data("ajax"), {name: input}, (data) ->
    results = []
    data.forEach (item) ->
      results.push({id: 1, name: item[0], score: item[1]})
    display_results(results, $ui)

search_old = (input, $ui) ->
  $button = $cur_input.parent().parent().find(".photo-upload-button")
  $button.prop("disabled", false)
  $button.children().css("color", "")
  f = new Fuse(list_of_names, {includeScore: true})
  result = f.search(input)
  results = ({id: item.item, name: list_of_names[item.item], score: item.score} for item in result)
  console.log(results)
  display_results(results, $ui)

display_results = (results, $ui) ->
  $ul = $ui.find("ul")
  $ul.children().remove()
  if results.length > 0
    for item in results.slice(0, 6)
      $span = $("<span>").addClass("name").text(item.name)
#      $li = $("<li>").attr("id", item.id).text("(#{Math.round((1-item.score)*100)}) ").append($span)
      $li = $("<li>").attr("id", item.id).text("(#{item.score})").append($span)
      $ul.append($li)
  else
      $li = $("<li>").text("Type to search for matches")
      $ul.append($li)
