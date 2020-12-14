# dsc.py  [![Badge](https://img.shields.io/pypi/v/dsc.py?color=3776AB&logo=python&style=for-the-badge)](https://pypi.org/project/dsc.py/)  [![Badge 2](https://img.shields.io/pypi/dm/dsc.py?color=3776AB&logo=python&style=for-the-badge)](https://pypi.org/project/dsc.py/)

A simple and easy to use, fully asynchronous wrapper for the dsc.gg API.

### Installation

```pip install dsc.py```

### Usage

Below you can find example usage of all of this library's methods and client initialization.  
For reference regarding objects returned by the library, [check this out](#objects)

#### Initialize the client

```py
import dsc

client = dsc.Client(key='YOUR_API_KEY')
```

#### Get a user

```py
user = await client.get_user(USER_ID)

print(f"This user joined dsc.gg on {user.created_at}")
```

#### Get a link

```py
link = await client.get_link('link')  # Can be either a slug or a full URL

print(f"This link owner's ID is: {link.owner_id}, and it leads to {link.redirect}")
``` 

#### Get an app

```py
app = await client.get_app(APP_ID)

print(f"This app's owner's ID is {app.owner_id} and it was created at {app.created_at}")
```

#### Get top links

```py
links = await client.get_top_links()

print(links[1].id)
```

#### Get a user's links (whitelist only)

```py
links = await client.get_user_links(USER_ID)

print(links[0].redirect)
```

#### Get a user's apps (whitelist only)

```py
apps = await client.get_user_apps(USER_ID)

print(any([app.verified for app in apps]))  # check if the user has any verified apps
```

#### Search (whitelist only)

```py
links = await client.search('search_query', limit=50)  # optional limit

print(len(links))
```

#### Create a link

You can get fancy with this one, and create an embed to use with the link, see below. Please note that the color will
not work, when creating, only when updating a link.

##### Create an embed

```py
embed = dsc.Embed(
    color=dsc.Color.red(),
    title='Embed title',
    image='image url',
    description='Embed description'
)
```

---
Anything other than the slug and the redirect is optional!
constructor.

```py
res = await client.create_link('link slug', 'redirect', embed=embed)

if res.status == 200:
    print('Link created!')
else:
    print('An error occurred.')
```

#### Update a link

Similar to creating, except the link slug has to be an existing link, there's no need to pass `type` in.  
Not passing some arguments into the embed will result in updating only these fields and leaving other ones as they are.

```py
updated_embed = dsc.Embed(color=dsc.Color.red())
await client.update_link('link slug', password='youshallnotpass', unlisted=True, embed=updated_embed)
```

#### Delete a link

```py
await client.delete_link('link slug')
```

### Objects

dsc.py includes 4 objects - User, Link, Embed and Color. Every attribute of the object will be listed, datetime values
are in UTC.

---

#### App

###### Attributes

- id: `int`
- owner_id: `int`
- verified: `bool`
- created_at: `datetime`
- key: `Optional[str]` (present only if you own the app)

###### Methods

- `to_dict()` - Return the object in the form of a dictionary

#### User

###### Attributes

- id: `int`
- premium: `bool`
- verified: `bool`
- joined_at: `datetime`
- staff: `bool`

###### Methods

- `to_dict()` - Return the object in the form of a dictionary

---

#### Link

###### Attributes

- id: `str`
- redirect: `str`
- owner_id: `int`
- embed: `dsc.Embed` (See the object below)
- editors: `List[int]`
- created_at: `datetime`
- type: `str` ('bot', 'server', 'template' or 'link')
- unlisted: `str`
- disabled: `bool`
- bumped_at: `datetime`
- domain: `str`

###### Methods

- `to_dict()` - Return the object in the form of a dictionary

---

#### Embed

Returned in responses or user created, embeds are a way to make your links stand out.

###### Attributes

- color: `dsc.Color` (See the object below)
- title: `str`
- description: `str`
- image `str` (image URL)

###### Methods

- `to_dict()` - Return the object in the form of a dictionary

###### Class methods

- `from_dict(data: dict)` - Return an Embed object initialized with values from the dictionary

---

#### Color

This is extremely similar to discord.py's Color, though allows passing strings as well.  
All discord.py built-in color class-methods are here too, ex. `dsc.Color.red()`

###### Attributes

- value: `int`

###### Methods

- `to_dict()` - Return the object in the form of a dictionary

###### Class methods

- [just like discord.py](https://discordpy.readthedocs.io/en/latest/api.html?highlight=color#discord.Colour.teal)

### Contributing

This package is opensource so anyone with adequate python experience can contribute to this project!

### Reporting Issues

If you find any error/bug/mistake with the package or in the code feel free to create an issue and report
it [here.](https://github.com/itsmewulf/dsc.py/issues)

### Fix/Edit Content

If you want to contribute to this package, fork the repository, make your changes and then simply create a Pull Request!

### Contact

If you want to contact me:  
**Mail -** ```wulf.developer@gmail.com```<br>
**Discord -** ```wulf#9632```
