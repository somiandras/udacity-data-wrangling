# Data Wrangling Project<br><small>András Somi, 2017. July</small>

## Data

__Data:__ `budapest_hungary_inner.osm` (107 MB)

__Source:__ [https://mapzen.com/data/metro-extracts/metro/budapest_hungary/](https://mapzen.com/data/metro-extracts/metro/budapest_hungary/)

I created a custom Metro extract on Mapzen for the inner parts of Budapest, capitol of Hungary. The available basic extract of Budapest area was way bigger than this exercise requires (close to 1GB) and also contained areas that in reality are not part of the city (that may cause conflicts in postcodes or street name duplications).

I live in the city, I have a general understanding of the naming conventions, special characters, etc. Also the different language makes it difficult to simply reuse code snippets from the examples, so I need to thoroughly think through every piece of it (and fight our usual fight with character encodings...)

## Auditing data

First, to have a general understanding of the data I ran through the whole xml counting the occurences of different attributes by tags and the overall count of the different tags. The dataset seems to be pretty uniform, ie. the different type of tags tend to have the same set of attributes for all the instances. For `node` tags `uid` and `username` attributes are missing in a tiny fraction of the cases.

```
TAG AND ATTRIBUTE COUNTS:

{'bounds': {'maxlat': 1, 'maxlon': 1, 'minlat': 1, 'minlon': 1},
 'member': {'ref': 68919, 'role': 68919, 'type': 68919},
 'nd': {'ref': 547248},
 'node': {'changeset': 422629,
          'id': 422629,
          'lat': 422629,
          'lon': 422629,
          'timestamp': 422629,
          'uid': 422611,
          'user': 422611,
          'version': 422629},
 'osm': {'generator': 1, 'timestamp': 1, 'version': 1},
 'relation': {'changeset': 7098,
              'id': 7098,
              'timestamp': 7098,
              'uid': 7098,
              'user': 7098,
              'version': 7098},
 'tag': {'k': 402982, 'v': 402982},
 'way': {'changeset': 75148,
         'id': 75148,
         'timestamp': 75148,
         'uid': 75148,
         'user': 75148,
         'version': 75148}}
```

But the bogger part of the data is stored in `tag` tags as key-value pairs in the `k` and `v` attributes. Let's look into these.

### Auditing street names

The first candidate for auditing is street names as this is the field where the most error might occur in the data.

#### Gold standard of street types

For a 'gold standard' of types of public places I used the information from [Wikipedia](https://hu.wikipedia.org/wiki/K%C3%B6zter%C3%BClet). This seems to be a complete, official list of the Hungarian names for different types of streets, roads and other public areas. I copied it into a `txt` file, from that I can extract the official list of types in a set.

```
{'lakótelep', 'utca', 'határút', 'orom', 'erdősor', 'körtér', 'rakpart', 'út', 'üdülőpart', 'part', 'átjáró', 'dűlőút', 'lejáró', 'ösvény', 'sétány', 'forduló', 'liget', 'tér', 'árok', 'mélyút', 'sor', 'sikátor', 'sugárút', 'lejtő', 'körönd', 'kapu', 'határsor', 'gát', 'pincesor', 'dűlő', 'park', 'köz', 'udvar', 'körút', 'lépcső', 'fasor'}
```

Pretty long, but the majority of them are fairly rare in the reality. I expect most of the datapoints in my dataset to end with _'utca'_ (street), _'út'_ (road) or _'tér'_ (square). (Maybe it's worth noting that in Hungarian we just put the type after the name of the street like 'Ilka _utca_' or 'Döbrentei _tér_', just as in English.)

#### Checking street types

Turns out the dataset is pretty clean... Even though I found 18 names that don't fit into any of the official categories, most of them actually make sense as these are grammatical variations of some basic types (eg. _'útja'_ means the road of someone or something, so absolutely valid). 

The rest are some unique places like a castle (yes, there are castles in Budapest!) with their unique names.

```
UNEXPECTED STREET NAMES:

{'Erzsébet királyné útja',
 'Ferenciek tere',
 'Hadak útja',
 'Harminckettesek tere',
 'Ifjúság útja',
 'Kucsma', <--- THIS IS INCORRECT
 'Kunigunda útja',
 'Magyar tudósok körútja',
 'Margitsziget',
 'Nagy Lajos király útja',
 'Népliget',
 'Népliget aluljáró',
 'Rákos-patak',
 'Rákospalotai körvasútsor',
 'Rózsák tere',
 'Vajdahunyadvár',
 'Vigadó téri hajóállomás',
 'Árpád fejedelem útja'} 
```

We have only one entry that is suspicious: _'Kucsma'_. That's actually the name of the street not the type, and apparently _'utca'_ (street) is missing from the end. _'Kucsma utca'_ occures seven times in the dataset.

```
...
 'Kruspér utca': 2,
 'Krúdy Gyula utca': 4,
 'Kucsma': 1,
 'Kucsma utca': 7,
 'Kulacs utca': 3,
 'Kulpa utca': 8,
...
```

#### Capital letters

The search also brought up a few cases where the street name starts with lower case letter. This should be also handled before uploading the dataset to a database.

```
...
 'Zöldmáli lejtő': 7,
 'dessewffy utca': 1,
 'podmaniczky utca': 1,
 'szabolcs utca': 1,
 'százados út': 1,
 'Ábel Jenő utca': 4,
...
```


### Auditing postcodes

In Hungary we use four-digit postcodes. All Budapest postcodes start with 1 and the second and third digit denotes the number of district. There are 23 districts in the city, so the inner two digits should be between 01 and 23, except for the island called Margitsziget, where the inner two digits are 00. 

There are no residential areas on the island but there are some cultural and sports facilities so we should still expect a few 00s to pop up in the dataset. ([The Districts of Budapest (Wikipedia)](https://en.wikipedia.org/wiki/List_of_districts_in_Budapest))

Based on these criteria four odd postcodes popped up in the audit. In the last one 'H' denotes Hungary in an international postcode format. It's a pattern we can easily correct programatically in the dataset. 

`1503` and `1507` are most likely typos for `1053` and `1057` (confirmed by the street names) while `1476` seems to be a valid postcode for some reason even though it does not seem to adhere to the standard format (but Google also gives [valid results](https://www.google.com/search?q=1476+budapest+%C3%BCll%C5%91i+%C3%BAt&oq=1476+budapest+%C3%BCll%C5%91i+%C3%BAt+&aqs=chrome..69i57j69i59.2827j0j9&sourceid=chrome&ie=UTF-8))

```
{'1476': {'count': 1, 'tags': ['Üllői út']},
 '1503': {'count': 1, 'tags': ['Kérő utca']},
 '1507': {'count': 1, 'tags': ['Irinyi József utca']},
 'H-1026': {'count': 2, 'tags': ['Pasaréti út', 'Pasaréti út']}}
```



