"""
A simple example script to get all posts on a user's timeline.
Originally created by Mitchell Stewart.
<https://gist.github.com/mylsb/10294040>
"""
import facebook
import requests


def some_action(post):
    """Here you might want to do something with each post. E.g. grab the
    post's message (post['message']) or the post's picture (post['picture']).
    In this implementation we just print the post's created time.
    """
    print(post["created_time"])


# You'll need an access token here to do anything.  You can get a temporary one
# here: https://developers.facebook.com/tools/explorer/
access_token = "EAASGlbun1PcBAAeq1JE7vHSnAU2ubnQhouKbut8ZCRlVM37wxZA5dtosZAirsPc2V5NcUbZCZAF8rSvnGyLLZChwkSWrtPdrWYZCd95o3rHVgHl3UcBCOUIFCZAyMStqmZBltrjSfr8uEVa1vVLe1QftLW8tRKn7p9ZC4ZC5e6bgZBQqM8ZCdEyjEZCvrDwpFj1QijxcO6XzvGTF2ZBgNZCJsCcHHtmoqjYsTXcNbgZA6ydN1cSXq0lzaZB9nFE0uSvMEjNwIR3EAJ2dN4ZAULARQZDZD"
# Look at Bill Gates's profile for this example by using his Facebook id.
user = "Christo Strydom"

graph = facebook.GraphAPI(access_token)
graph = facebook.GraphAPI(access_token=access_token)
friends = graph.get_connections(id="christo.strydom.1004", connection_name="friends")

profile = graph.get_object("christo.strydom.1004")
posts = graph.get_connections(profile["id"], "posts")

import requests

user_id = "christo.strydom.1004"  # Replace USER-ID with the actual user ID

# https://www.facebook.com/groups/496689524844214/members
url = f"https://graph.facebook.com/groups/{user_id}/posts"

params = {"access_token": access_token}

response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Print the content of the response
    print(response.json())
else:
    print(f"Error: {response.status_code}")
    print(response.text)  # Print the error message
# Each given id maps to an object the contains the requested fields.


for place in places["data"]:
    print("%s %s" % (place["name"].encode(), place["location"].get("zip")))

# Wrap this block in a while loop so we can keep paginating requests until
# finished.
while True:
    try:
        # Perform some action on each post in the collection we receive from
        # Facebook.
        [some_action(post=post) for post in posts["data"]]
        # Attempt to make a request to the next page of data, if it exists.
        posts = requests.get(posts["paging"]["next"]).json()
    except KeyError:
        # When there are no more pages (['paging']['next']), break from the
        # loop and end the script.
        break
