# TODO: http://classify.oclc.org/classify2/ClassifyDemo?search-standnum-txt=978-0060009762&startRec=0
# TODO: Use that website to see if we can get the dewey decimal identification for the books
# The DDC is heirarchical system, so we can get a good proxy for what areas are "under-covered" by checking which numbers don't exist
# May get some mileage out of the FAST Subject Heading?
# NOTE: At the very least, the DDC number could be a decent factor for any future ml models
#
# I expect the DDC approach will not be complete for a couple reasons:
#  1) Some "topics" are over/under-clustered (See Wikipedia DDC section on religion for an example)
#    - Basically a wide variety of topics can appear under 1 number while one topic gets spread among several numbers
#  2) Topics can be classified under multiple different numbers
#  3) It's not guaranteed that the books will have a DDC number in the system
#
# Measuring dissimilarity:
#  1) Farthest left-digit that is different
#  2) Farthest average left-digit difference
#  3) Exponentially weight the difference of the digits (so that first digit differences are weighted more than last digit differences)

# TODO: See if there's a way I can use the "FAST" subject information
# TODO: See how these operations change if I select one of the books

import anyconfig
import goodreads
import goodreads.book
import goodreads.client
import math
import requests
import xmltodict

class GoodreadsList:
    def __init__(self, client, shelf_id):
        self._client = client
        self._api_path = "review/list/{}/?page={{}}".format(shelf_id)

    def __iter__(self):
        """
        Lazily query the goodreads api to extract all information about books in this shelf
        """
        current_page = 0
        max_pages = 1
        while current_page < max_pages:
            current_page += 1
            shelf = self._client.request(self._api_path.format(current_page), self._client.query_dict)['books']

            for book in shelf['book']:
                yield goodreads.book.GoodreadsBook(book, self._client)

            max_pages = int(shelf['@numpages'])


class Client(goodreads.client.GoodreadsClient):

    def get_list(self, shelf_id):
        return GoodreadsList(self, shelf_id)


conf = anyconfig.load("conf.yaml")
GOODREADS_API_KEY = conf.get('api_key')
GOODREADS_SECRET = conf.get('api_secret')

gc = Client(GOODREADS_API_KEY, GOODREADS_SECRET)

# search = 'http://classify.oclc.org/classify2/Classify?isbn=978-0060009762'
# read = 'http://classify.oclc.org/classify2/Classify?isbn={}&summary=true'
read = 'http://classify.oclc.org/classify2/Classify?isbn={}{}'

def get_isbn(book):
    return book.isbn13 or book.isbn

def verify_classification_data(resp):
    if not 'classify' in resp:
        return False
    if not ('works' in resp['classify'] or 'recommendations' in resp['classify']):
        return False
    return True

def extract_ddc_number(ddc):
    # TODO: This isn't an accurate way of producing a ddc value
    # For "Napoleon", it can sometimes produce "B"
    if isinstance(ddc, list):
        ddcs = [extract_ddc_number(num) for num in ddc]
        for ddc in ddcs:
            try:
                float(ddc)
                return ddc
            except:
                continue

    elif '@nsfa' in ddc:
        return ddc['@nsfa']
    elif '@sfa' in ddc:
        return ddc['@sfa']

    raise Exception("No ddc in ddc structure - {}".format(ddc))

def extract_fast_subjects(fast):
    headings =  fast.get('headings', {}).get('heading', [])
    if not isinstance(headings, list):
        headings = [headings]
    return [subject['#text'] for subject in headings]

def resolve_disambiguation(resp):
    if 'recommendations' in resp:
        return resp

    # TODO: '@wi' may not always be in the response?
    wi = next(wi['@wi'] for wi in resp['works']['work'] if '@wi' in wi)
    resp = xmltodict.parse(requests.get("http://classify.oclc.org/classify2/Classify?wi={}".format(wi)).content)
    return resp['classify']

def classify_book_oclc(isbn, summary=False):
    resp = xmltodict.parse(requests.get(read.format(isbn, summary and "&summary=true" or "")).content)
    if not verify_classification_data(resp):
        return None, None

    resp = resolve_disambiguation(resp['classify'])
    ddc = extract_ddc_number(resp['recommendations']['ddc']['mostPopular'])
    return ddc, extract_fast_subjects(resp['recommendations'].get('fast', {}))

# Some books have multiple results in searches
# books = {}
# for book in gc.get_list(81192485):
#     isbn = get_isbn(book)
#     try:
#         ddc, fast = classify_book_oclc(isbn)

#     except Exception as e:
#         print("Exception on book {} ({}) - {}".format(book.title, isbn, e))

#     if ddc is None:
#         continue

#     books[isbn] = {
#         'title': book.title,
#         'ddc': ddc,
#         'fast': fast
#     }

# # for isbn, data in books.items():
# #     print("{} ({}) = {}".format(data['title'], isbn, data['ddc']))

# choices = {}
# # print('-'*20)
# with open('data/choices.csv') as f:
#     for isbn in f:
#         isbn = isbn[:-1].replace('-', '')
#         title = gc.book(isbn=isbn).title
#         try:
#             ddc, fast = classify_book_oclc(isbn)
#         except Exception as e:
#             print("Exception on book {} ({}) - {}".format(title, isbn, e))

#         if ddc is None:
#             continue

#         choices[isbn] = {
#             'title': title,
#             'ddc': ddc,
#             'fast': fast
#         }
# # for isbn, data in choices.items():
# #     print("{} ({}) = {}".format(data['title'], isbn, data['ddc']))

# TODO: Cache the results
import json
cache = {}
with open('data/ddc_cache.json') as f:
    cache = json.load(f)

books = cache['books']
choices = cache['choices']

# Split out the sample data from source
with open('data/samples.csv') as f:
    samples = [isbn[:-1].replace('-', '') for isbn in f]
choices = {
    isbn: books.pop(isbn) for isbn in samples
}

# Measure a book as "most different" if it has the highest average distance to all other books
# Chaos > The Information > The Case Against Reality > The Shaping Of Us > Talking to Strangers
# Turing > Organized Mind > Antifragile > Justice > Dream of Reason (4.286 / _)
# avg = {}
# for isbn in choices:
#     count = 0
#     for comp in books:
#         if comp == isbn:
#             continue
#         count += abs(float(choices[isbn]['ddc']) - float(books[comp]['ddc']))
#     avg[isbn] = count / (len(books) - 1)
# rec = list(map(lambda k: (k, avg[k]), sorted(avg, key=avg.get, reverse=True)))
# # for r, sim in rec:
# #     print("{} - {}".format(choices[r]['title'], sim))

# Measure a book as "most different" if it's nearest neighbor is farthest away
# Tyranny of Metrics > Case Against Reality > The Third Plate > The Information > End Times
# Dream of Reason > Babel > Constitution Today > History of White People > Antifragile (5.523 / _)
# near = {}
# for isbn in choices:
#     dist = 10000
#     for comp in books:
#         if comp == isbn:
#             continue
#         dist = min(dist, abs(float(choices[isbn]['ddc']) - float(books[comp]['ddc'])))
#     near[isbn] = dist
# rec = list(map(lambda k: (k, near[k]), sorted(near, key=near.get, reverse=True)))
# # for r, sim in rec:
# #     print("{} - {}".format(choices[r]['title'], sim))

# Measure a book as "most different" if the ddc path has the fewest existing books
# Utopia of Rules > Grand Strategy > Most Elegant Equation > Money > The Ball is Round
# Inside the Black Box > Conquest > Red Card > Organized Mind > Imperial Twilight (7.143 / _)
# def produce_trie(isbns, books, level):
#     if len(isbns) == 1:
#         return [isbns[0]]

#     trie = {}
#     for isbn in isbns:
#         try:
#             ddc = books[isbn]['ddc'][level]
#         except:
#             ddc = ''
#         if ddc not in trie:
#             trie[ddc] = []
#         trie[ddc].append(isbn)

#     for ch, vals in trie.items():
#         if ch != '':
#             trie[ch] = produce_trie(vals, books, level + 1)
#     trie['count'] = len(isbns)
#     return trie

# for book in books.values():
#     book['ddc'] = book['ddc'].replace('.', '')
# trie = produce_trie(books.keys(), books, 0)

# tries = {}
# for isbn in choices:
#     count = 0
#     node = trie
#     for ch in choices[isbn]['ddc'].replace('.', ''):
#         if ch not in node:
#             break
#         count /= 10
#         if isinstance(node, list):
#             count += len(node)
#             break
#         count += node['count']
#         node = node[ch]
#     tries[isbn] = count
# rec = list(map(lambda k: (k, tries[k]), sorted(tries, key=tries.get)))
# # for r, sim in rec:
# #     print("{} - {}".format(choices[r]['title'], sim))

# TODO: Measure a book as "most different" is it has a large number of high dissimilarity scores against other books
# Chaos > Information > The Case Against Reality > The Shaping of Us > Hello World
# Turing > Organized Mind > Antifragile > Dream of Reason > Justice (4.571 / _)
dists = {}
for isbn in choices:
    count = 0
    for comp in books:
        if comp == isbn:
            continue
        dist = abs(float(choices[isbn]['ddc']) - float(books[comp]['ddc']))
        if dist > 500:
            count += 10
        elif dist > 400:
            count += 7
        elif dist > 300:
            count += 4
        elif dist > 200:
            count += 1
        elif dist > 100:
            count -= 3
        elif dist > 0:
            count -= 5
        else:
            count -= 7
    dists[isbn] = count
rec = list(map(lambda k: (k, dists[k]), sorted(dists, key=dists.get, reverse=True)))
# for r, sim in rec:
#     print("{} - {}".format(choices[r]['title'], sim))


# TODO: Measure a book as "most different" if the sum of the log of the distances is the highest
# Information > Chaos > The Case Against Reality > The Shaping of Us > A History of Languages
# Turing > Organized Mind > Antifragile > Dream of Reason > Justice (4.762 / _)
# avg = {}
# for isbn in choices:
#     count = 0
#     for comp in books:
#         if comp == isbn:
#             continue
#         val = abs(float(choices[isbn]['ddc']) - float(books[comp]['ddc']))
#         if val:
#             count += math.log(val)
#     avg[isbn] = count
# rec = list(map(lambda k: (k, avg[k]), sorted(avg, key=avg.get, reverse=True)))
# # for r, sim in rec:
# #     print("{} - {}".format(choices[r]['title'], sim))

# For any given book, the isbn query will either:
#  1) return the book page
#  2) return a disambiguation page
#
# The book page can be reached from disambiguation by selecting a '@wi' or '@owi' from the "works" field

# Compare the produced recommendations with the "test" ratings
with open('data/sample_ratings.csv') as f:
    ratings = [isbn[:-1].replace('-', '') for isbn in f]
total = 0
for i, (isbn, _) in enumerate(rec):
    rank = ratings.index(isbn)
    total += abs(rank - i)
    print("{} - {} ({}, {})".format(choices[isbn]['title'], rank - i, i, rank))
print("avg: {}".format(total / len(rec)))
