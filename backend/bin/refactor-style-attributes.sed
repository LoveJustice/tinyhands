#!/usr/bin/env gsed --file

# Sed script to replace 'text-align' styles with a corresponding 'class' value in HTML
# elements. For example, 'style="text-align: center"' will be replaced with
# 'class="text-center"'. It also works with 'right' and 'left' alignments.
#
# This script requires Gnu Sed (gsed on my machine).
#
# If a 'class' attribute already exists, the new alignment class is added to the current
# list of classes in the attribute. If additional styles are present in the 'style'
# attribute, they are left in place.  In rare cases (see comments, below) a text-align
# attribute may be left in place for correctness. Post-process the resulting text (e.g.,
# with grep(1)) to catch such cases.

# Simple case: lines without a 'class' attribute.
/class/! s/style="\(.*\)text-align:\s*\(center\|left\|right\)\(.*\)"/class="text-\2" style="\1\3"/

# Lines with 'class' attribute followed by 'style' attribute. Preserve: (1) styles other
# than text-align, and (2) content between the elements. The '[^>]*' in the address
# pattern prevents applying the replacement on lines having multiple elements in which the
# first has a 'class' attribute and the other has a 'style'. Without this, the text-align
# class is applied to the wrong element (the one with the 'class' attribute). It seemed
# better to leave the style in place, than replace it incorrectly.
/class[^>]*style/ s/class="\(.*\)"\(.*\)style="\(.*\)text-align:\s*\(center\|left\|right\)\(.*\)"/class="\1 text-\4"\2style="\3\5"/

# Lines with 'style' attribute followed by 'class' attribute. Works similarly to the
# previous command.
/style[^>]*class/ s/style="\(.*\)text-align:\s*\(center\|left\|right\)\(.*\)"\(.*\)class="\(.*\)"/style="\1\3"\4class="text-\2 \5"/

# When a style attribute contains multiple styles and the text-align attribute appears
last, the previous replacements leave behind a superfluous semicolon (and, sometimes, a
space). Remove these.
s/style="\([^"]*\);\s*"/style="\1"/

# If a style attribute has been emptied, remove it entirely.
s/style=""//
