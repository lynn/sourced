from configparser import ConfigParser
import sourced

# Fetch a JSON file from the web, and save it to todos.json, and use it.
# Next time, the local todos.json is used instead of fetching the file.
photos = sourced.json('photos.json', url='https://jsonplaceholder.typicode.com/photos')
print(photos[0]['title'])

# Same, but with UTF-8 text.
alice = sourced.text('alice.txt', url='http://www.gutenberg.org/files/11/11-0.txt')
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
