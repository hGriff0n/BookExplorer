
import json
import math
import numpy
from numpy.linalg import norm
import statistics

with open('data/cache.json') as f:
    books = json.load(f)

choices = books.pop('choices', {})
for isbn in choices:
    choices[isbn] = (choices[isbn][0], numpy.array(choices[isbn][1]))

books = books['books']
for isbn in books:
    books[isbn] = (books[isbn][0], numpy.array(books[isbn][1]))

with open('data/samples.csv') as f:
    samples = [isbn[:-1].replace('-', '') for isbn in f]

with open('data/sample_ratings.csv') as f:
    ratings = [isbn[:-1].replace('-', '') for isbn in f]

choices = {
    isbn: books.pop(isbn) for isbn in samples
}


def cosine_similarity(a, b):
    a = numpy.array(a)
    b = numpy.array(b)
    product = numpy.inner(a, b)/(norm(a)*norm(b))
    return product[0][0]

# TODO: Improve this code to enable further development (what do i mean by this?)

# Measure a book as "most different" if the average similarity against all books is smaller
# Case Against Reality > Tyranny of Metrics > You'll See This Message When It Is Too Late > The Sports Gene > The Shaping of Us
# Justice > Red Card > Inside the Black Box > Light > Babel (7.238 / 7.3)
# avg = {}
# num_books = len(books) - 1
# for isbn in choices:
#     count = 0
#     for comp in books:
#         if comp == isbn:
#             continue
#         count += cosine_similarity(books[comp][1], choices[isbn][1])
#     avg[isbn] = count / num_books
# rec = list(map(lambda k: (k, avg[k]), sorted(avg, key=avg.get)))
# # for r, sim in rec:
# #     print("{} - {}".format(choices[r][0], 1 - sim))

# Measure a book as "most different" if it has a large number of high dissimilarity scores against other books
# Case Against Reality > Tyranny of Metrics > The Shaping of Us > You'll See This Message When It Is Too Late > Hello World
# Justice > Red Card > Inside the Black Box > Light > The Organized Mind (7.048 / 7.1)
# percentile = {}
# for isbn in choices:
#     count = 0
#     for comp in books:
#         if comp == isbn:
#             continue
#         sim = 1 - cosine_similarity(books[comp][1], choices[isbn][1])
#         # Weighting can be modified to allow for many somewhat different to override one very different (or vice versa)
#         if sim > 0.9:
#             count += 100
#         elif sim > 0.7:
#             count += 10
#         elif sim > 0.5:
#             count += 1
#         # We can also punish books which are too similar
#         # elif sim < 0.1:
#         #     count -= 150
#         elif sim < 0.3:
#             count -= 20
#     percentile[isbn] = count
# rec = list(map(lambda k: (k, percentile[k]), sorted(percentile, key=percentile.get, reverse=True)))
# # for r, sim in rec:
# #     print("{} - {}".format(choices[r][0], sim))

# Measure a book as "most different" if it is the least "most-close" book (highest min difference)
# The Sports Gene > You'll See This Message When It Is Too Late > VC > Talking to Strangers > Hello World
# Justice > Red Card > Babel > The History of White People > Light (6.190 / 6.5)
# spread = {}
# for isbn in choices:
#     spread[isbn] = min(1 - cosine_similarity(books[comp][1], choices[isbn][1]) for comp in books if comp != isbn)
# rec = list(map(lambda k: (k, spread[k]), sorted(spread, key=spread.get, reverse=True)))
# # for r, sim in rec:
# #     print("{} - {}".format(choices[r][0], sim))

# Measure a book as "most different" if the some of the log of the similarities is the lowest (as it goes negative)
# Case Against Reality > Tyranny of Metrics > The Shaping of Us > Hello World > You'll See This Message When It Is Too Late
# Justice > Red Card > Inside the Black Box > The Organized Mind (7.143 / 6.7)
# avg = {}
# num_books = len(books) - 1
# for isbn in choices:
#     avg[isbn] = 0
#     for comp in books:
#         if comp == isbn:
#             continue
#         avg[isbn] += math.log(cosine_similarity(books[comp][1], choices[isbn][1]))
# rec = list(map(lambda k: (k, avg[k]), sorted(avg, key=avg.get)))
# # for r, sim in rec:
# #     print("{} - {}".format(choices[r][0], sim))

# Measure a book as "most different" if the some of the log of the differences (1-similarity) is the highest
# Case Against Reality > You'll See This Message When It Is Too Late > The Sports Gene > Tyranny of Metrics > The Shaping of Us
# Justice > Red Card > Inside the Black Box > Babel > Light (7.238 / 7.1)
avg = {}
num_books = len(books) - 1
for isbn in choices:
    avg[isbn] = 0
    for comp in books:
        if comp == isbn:
            continue
        avg[isbn] += math.log(1 - cosine_similarity(books[comp][1], choices[isbn][1]))
rec = list(map(lambda k: (k, avg[k]), sorted(avg, key=avg.get, reverse=True)))
# for r, sim in rec:
#     print("{} - {}".format(choices[r][0], sim))

total = 0
for i, (isbn, _) in enumerate(rec):
    rank = ratings.index(isbn)
    total += abs(rank - i)
    print("{} - {} ({}, {})".format(choices[isbn][0], rank - i, i, rank))
print("avg: {}".format(total / len(rec)))
