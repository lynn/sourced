# sourced

I don't like writing this in my Python scripts every time:

```py
import json, os, requests
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

And offers some other handy behavior.

# Documentation

## Basic usage

Pass `url`, and optionally `headers`, to fetch and decode files from the web.
Use `encoding` to set the encoding for text and JSON. It defaults to `utf-8`.

```py
t = sourced.text('merci.txt', url=text_url, headers={'Accept-Language': 'fr'})
s = sourced.text('sozai.txt', url=sjis_url, encoding='shift_jis')
j = sourced.json('okay.json', url=json_url, headers={'Authorization': token})
b = sourced.binary('data.bin', url=binary_url)
assert isinstance(s, str)
assert isinstance(j, dict)
assert isinstance(b, bytes)
```

Alternatively, use `create=file_creating_function`. This function should
return a deserialized result (so, a `dict` rather than a string, for JSON).

```py
def default_json(): return {'meow': 123}
j = sourced.json('my.json', create=default_json)
```

## Cache Invalidation

Pass `max_age='2 weeks'` to invalidate cached files after 2 weeks.
[pytimeparse](https://github.com/wroberts/pytimeparse) is used to parse
the provided time delta.

```py
stuff = sourced.json('stuff.json', url=my_url, max_age='5 days')
```

## JSON paths

When you only need part of the data at `url`, you can provide a JSON path
to select the parts you want. The JSON path library used is
[jsonpath-rw](https://github.com/kennknowles/python-jsonpath-rw).

Use `find=path` to get an array of matches:

```py
sourced.json('titles.json', url=url, find='[:10].title')
```

Use `pick=path` to keep just the first match:
```py
sourced.json('titles.json', url=url, pick='[?(@.id == 99)]')
```

## Pagination

### Predefined pages

If `url` is a list, the results are concatenated with `+`. This is
useful for text or JSON endpoints that return arrays.

```py
sourced.json('combi.json', url=[url1, url2])
sourced.text('combi.txt', url=[url3, url4])
```

### URL-numbered pages

If `url` is `https://blah.com/foo/%p1`, then requests are made for
`https://blah.com/foo/1`, `https://blah.com/foo/2`, … until the result is
empty text / an empty JSON array.

Use `%p0` to start numbering pages from 0 instead.

```py
sourced.json('tags.json', url='https://testbooru.donmai.us/tags.json?limit=500&page=%p1')
```

### JSON-pathed pages

If using JSON and `next_path` is a JSON path, it is used to retrieve a URL
for the next page until it is `null`.

```py
kanji = sourced.json('kanji.json',
    url='https://api.wanikani.com/v2/subjects?types=kanji',
    headers={'Wanikani-Revision': '20170710',
             'Authorization': 'Bearer %s' % wk_token},
    find='data[*].data.characters', next_page='pages.next_url')
```

### Custom next-path function

If `next_path` is a function, it is called with the decoded (e.g. JSON object)
result to get the next page URL.

```py
f = lambda json: base_url + '&start_from=' + json['next_page_start']
sourced.json('a.json', url=base_url, next_page=f)
```
