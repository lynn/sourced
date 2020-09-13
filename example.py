from configparser import ConfigParser
import os
import sourced

# Fetch a JSON file from the web, and save it to todos.json, and use it.
# Next time, the local todos.json is used instead of fetching the file.
photos = sourced.json('photos.json', url='https://jsonplaceholder.typicode.com/photos')
print(photos[0]['title'])

# Same, but with UTF-8 text.
alice = sourced.text('alice.txt', url='http://www.gutenberg.org/files/11/11-0.txt', max_age='5 seconds')
print(alice.lower().count('rabbit'))

# Same, but with the results of an expensive operation.
def expensive_operation():
    """Crunch a lot of numbers."""
    return [pow(2, k, 24793) for k in range(100000)]

powers = sourced.json('powers.json', create=expensive_operation)
print(powers[87654])

# CSV is another supported format:
csv_url = 'http://samplecsvs.s3.amazonaws.com/TechCrunchcontinentalUSA.csv'
with sourced.csv('funding.csv', url=csv_url) as reader:
    print(next(reader))

# Or use csv.DictReader:
with sourced.csv_dict('funding.csv', url=csv_url) as reader:
    print(next(reader))

# .ini files:
conf = sourced.ini('my_config.ini', default={'section': {'foo': 123}})
print(conf.getint('section', 'foo'))

titles = sourced.json('titles.json', url='https://jsonplaceholder.typicode.com/photos', find='[*].title')
print(titles[:3])

# Cursor pagination (WaniKani API):
wk_token = os.environ.get('WK_TOKEN')
if wk_token:
    headers = {'Wanikani-Revision': '20170710', 'Authorization': 'Bearer %s' % wk_token}
    k = sourced.json('kanji.json', url='https://api.wanikani.com/v2/subjects?types=kanji',
            headers=headers, find='data[*].data.characters', next_page='pages.next_url')
    print(len(k))

# Query param / URL pagination (Danbooru API):
tags = sourced.json('tags.json', url='https://testbooru.donmai.us/tags.json?limit=500&page=%p1', find='[*].name')
print(len(tags), 'tags.')

