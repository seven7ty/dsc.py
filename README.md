# dsc.py
A simple and easy to use, fully asynchronous wrapper for the dsc.gg API.

### Installation 

Installing `dsc.py` is easy, just run `pip install dsc.py`!

### Usage 

`dsc.py` covers all routes in the dsc.gg API. You can find example usage of all of them below, and for detailed attributes of the objects returned, [go here.](#dscpy-objects)
Note that all the examples can be used for example with a discord.py bot, but for the sake of simplicity I decided to use plain async and asyncio.

#### Get a single link

```py
import dsc
import asyncio

client = dsc.Client()

link = asyncio.get_event_loop().run_until_complete(client.get_link("mycoollink")) # <-- Without the dsc.gg/ prefix

print(f"My link has {link.clicks} clicks, and redirects to {link.redirect}")

# Example output:
# My link has 47 clicks, and redirects to https://github.com/itsmewulf/dsc.py
```

#### Get a user's links

```py
import dsc
import asyncio

client = dsc.Client()

link = asyncio.get_event_loop().run_until_complete(client.get_links(548803750634979340)) # <-- Discord User ID

# link is now a list of Link objects from the previous example
```

#### Get a dsc.gg user

```py
import dsc
import asyncio

client = dsc.Client()

user = asyncio.get_event_loop().run_until_complete(client.get_user(548803750634979340)) # <-- Discord User ID

print(f"This user has {user.links} links, and his premium status is: {user.premium}")

# Example output:
# This user has 3 links, and his premium status is: False
```

#### Get a user's announcements

```py
import dsc
import asyncio

client = dsc.Client()

announcements = asyncio.get_event_loop().run_until_complete(client.get_announcements(548803750634979340)) # <-- Discord User ID

# I couldn't find a reference announcement, however i know its a list
```

## Authenticated section

Methods in this section require you to pass a Discord OAuth Token into the client constructor. Information on how to find your token can be found [here.](https://www.youtube.com/watch?v=xuB1WQVM3R8) Below is an example of using an authenticated client to create a link.

#### Create a link
```py
import dsc
import asyncio

client = dsc.Client("YOUR DISCORD USER TOKEN")

asyncio.get_event_loop().run_until_complete(client.create_link(link="mycoolthing", redirect="https://mycoolbotinvite.gg", link_type="bot")) 

# link_type passed above specifies what kind of link it is, it has to be lowercase and one of these - [bot, server, template]

# The code above will create a link dsc.gg/mycoolbot that leads to https://mycoolbotinvite.gg on your account
```

#### Update a link

Note that the link itself (ex. dsc.gg/mycoolbot) cannot be changed, this is an API limitation. The only thing you can change is the redirect and link type. You need to pass in the same parameters as above, here's an example:

```py
import dsc
import asyncio

client = dsc.Client("YOUR DISCORD USER TOKEN")

asyncio.get_event_loop().run_until_complete(client.update_link(link="mycoolthing", redirect="https://mycoolserverinvite.gg", link_type="server")) 

# The code above will update a link called mycoolthing by setting it's redirect to https://mycoolserverinvite.gg,
# we pass in link_type to make the API recognize the link is a server
```

#### Delete a link


```py
import dsc
import asyncio

client = dsc.Client("YOUR DISCORD USER TOKEN")

asyncio.get_event_loop().run_until_complete(client.delete_link(link="mycoolthing")) 

# The above code will delete a link called mycoolthing from your account
```

#### Transfer a link

```py
import dsc
import asyncio

client = dsc.Client("YOUR DISCORD USER TOKEN")

asyncio.get_event_loop().run_until_complete(client.transfer_link(link="mycoolthing", user_id=548803750634979340, comments="Giving it to my friend")) 

# The above code will transfer a link called mycoolthing to a user with the ID 548803750634979340,
# and the comment specifying the reason will be "Giving it to my friend". 
# The comment is optional, if omitted, the library passes an acceptable "None" by default.
```

## dsc.py objects

#### User 
- links: int
- premium: bool
- blacklisted: bool
- staff: Any

#### Link
- clicks: int
- unique: int (Unique clicks)
- type: str
- suspended: bool
- recent: tuple (User agent of the latest click: str, timestamp of the latest click: int)
- redirect: str 
- owner_id: int
- click_other: int or None (idk what this is honestly)
- agents: str (For advanced users, a gibberish string with user agents)
- embed: dsc.Embed (See below)

#### Embed
- title: str 
- description: str 
- saying: str (For example, "You have been invited to join a server!")
- image: str (Url to image associated)
- color: str (Hex color, ex. #efefef)

### Contributing 

This package is opensource so anyone with adequate python experience can contribute to this project!

### Report Issues
If you find any error/bug/mistake with the package or in the code feel free to create an issue and report it [here.](https://github.com/itsmewulf/dlabs.py/issues)

### Fix/Edit Content
If you want to contribute to this package, fork the repository, make your changes and then simply create a Pull Request!

### Contact
If you want to contact me -<br>
**Mail -** ```wulf.developer@gmail.com```<br>
**Discord -** ```wulf#9716```
