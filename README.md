# sourced

I don't like writing this in my Python scripts every time:

```py
import json
import os
import requests
photos_url = 'https://jsonplaceholder.typicode.com/photos'
photos_path = 'photos.json'

# Fetch the file if it doesn't exist yet.
if not os.path.isfile(photos_path):
    res = requests.get(photos_url)
    with open(photos_path, 'wb') as f:
        f.write(res.content)

# Then, use the local copy.
with open('photos.json') as f:
    photos = json.load(f)

print(photos[0]['title'])
```

So this little library lets you write:

```py
import sourced
photos_url = 'https://jsonplaceholder.typicode.com/photos'

photos = sourced.json('photos.json', url=photos_url)
print(photos[0]['title'])
```

And maybe more cool things, soon.
