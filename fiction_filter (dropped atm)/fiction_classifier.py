
# Producing the training sets will be the hardest aspect
# https://www.goodreads.com/list/show/134.Best_Non_Fiction_no_biographies_
#

# https://www.fictiondb.com/

"""
https://www.goodreads.com/list/show/8166.Books_You_Wish_More_People_Knew_About
https://www.goodreads.com/list/show/3.Best_Science_Fiction_Fantasy_Books
https://www.goodreads.com/list/show/1.Best_Books_Ever
https://www.goodreads.com/list/show/47.Best_Dystopian_and_Post_Apocalyptic_Fiction
https://www.goodreads.com/list/show/26495.Best_Woman_Authored_Books
https://www.goodreads.com/list/show/338.Immigrant_Experience_Literature
https://www.goodreads.com/list/show/823.Africa_fiction_and_nonfiction_
https://www.goodreads.com/list/show/15.Best_Historical_Fiction
https://www.goodreads.com/list/show/264.Books_That_Everyone_Should_Read_At_Least_Once
https://www.goodreads.com/list/show/301.Best_Middle_Ages_Books

https://www.goodreads.com/list/show/8342.You_Read_a_Book_about_What_
https://www.goodreads.com/list/show/2122.Medicine_and_Literature
https://www.goodreads.com/list/show/1058.Microhistory_Social_Histories_of_Just_One_Thing
https://www.goodreads.com/list/show/692.Best_Science_Books_Non_Fiction_Only
https://www.goodreads.com/list/show/281.Best_Memoir_Biography_Autobiography
https://www.goodreads.com/list/show/134.Best_Non_Fiction_no_biographies_
https://www.goodreads.com/list/show/101739.Best_of_21st_Century_Non_fiction
"""

# import anyconfig
import requests
import xmltodict

# from goodreads_frontend import api


# I have a dataset of ~10000 books from https://github.com/zygmuntz/goodbooks-10k
# I need to transform this into json

# TODO: Look at using pandas instead of csv
import csv
import json
import os
import xml

def transform_csv_to_json(csv_filepath, json_filepath):
    with open(csv_filepath, encoding='utf8') as books:
        reader = csv.DictReader(books)
        all_books = [book for book in reader]
        with open(json_filepath, 'w') as out:
            out.write(json.dumps(all_books, sort_keys=True, indent=4))

data_directory = os.path.join('fiction_filter', 'data')
csv_source_file = os.path.join(data_directory, 'all_books_src.csv')
json_source_file = os.path.join(data_directory, 'all_books_src.json')
goodreads_source_file = os.path.join(data_directory, 'all_books_id.json')
goodreads_info_file = os.path.join(data_directory, 'all_books_info.json')
goodreads_classification_file = os.path.join(data_directory, 'all_books_classification.json')

# TODO: Transform this method to instead query from goodreads and fill the json with the relevant goodreads data (description in particular)
def transform_json_src_to_goodreads(json_filepath, goodreads_filepath):
    def _transform_json_entry_to_goodreads(entry):
        return { 'goodreads_book_id': entry.get('goodreads_book_id'), 'original_title': entry.get('original_title') }

    with open(json_filepath) as f:
        all_books = [ _transform_json_entry_to_goodreads(book) for book in json.load(f) ]
        with open(goodreads_filepath, 'w') as out:
            out.write(json.dumps(all_books, sort_keys=True, indent=4))

def filter_goodreads_entry(entry):
    entry.pop('small_image_url', None)
    entry.pop('text_reviews_count', None)
    entry.pop('reviews_widget', None)
    entry.pop('ratings_count', None)
    entry.pop('marketplace_id', None)
    entry.pop('image_url', None)
    # entry.pop('edition_information', None)
    entry.pop('country_code', None)
    entry.pop('buy_links', None)
    entry.pop('book_links', None)
    entry.pop('average_rating', None)
    return entry

def extend_with_goodreads_information(src_filepath, output_filepath):
    def _color_book_info(entry):
        resp = requests.get('https://www.goodreads.com/book/show/{}/?format=xml'.format(entry['goodreads_book_id']), params={'key': 'FDOd988WsyILd59cob9KQ'})
        try:
            entry.update(filter_goodreads_entry(xmltodict.parse(resp.content)['GoodreadsResponse'].get('book', {})))
        except xml.parsers.expat.ExpatError:
            print('ExpatError: ' + entry['goodreads_book_id'])
        except KeyError:
            print('KeyError: ' + entry['goodreads_book_id'])
        return entry


    with open(src_filepath) as f:
        all_books = [ _color_book_info(book) for book in json.load(f) ]
        with open(output_filepath, 'w') as out:
            out.write(json.dumps(all_books, sort_keys=True, indent=4))

def filter_goodreads_information(output_filepath):
    with open(output_filepath) as f:
        all_books = [ filter_goodreads_entry(book) for book in json.load(f) ]
    with open(output_filepath, 'w') as f:
        f.write(json.dumps(all_books, sort_keys=True, indent=4))

def str_to_bool(s):
    return s.lower() in ['yes', 'true', 'y', 't']

def add_result_information(info_filepath, output_filepath):
    def _classify_book(entry):
        print("Title: {}".format(entry.get('title')))
        print("Url: {}".format(entry.get('url')))
        genre = input("genre: ")
        fiction = str_to_bool(input("fiction: "))
        entry.update({'classification': {'genre': genre, 'is_fiction': fiction}})
        return entry
    with open(info_filepath) as f:
        all_books = [ _classify_book(book) for book in json.load(f) ]
    with open(output_filepath, 'w') as f:
        f.write(json.dumps(all_books, sort_keys=True, indent=4))

def mark_all_unexpected_genres(filepath, exepected_genres):
    with open(filepath) as f:
        for book in json.load(f):
            if book.get('classification', {}).get('genre', '') not in exepected_genres:
                print("Unexpected genre for book {}".format(book['goodreads_book_id']))
            if book.get('classification', {}).get('genre', '') in ['Fiction', 'Noniction']:
                print("No sub-genre for book {}".format(book['goodreads_book_id']))

# extend_with_goodreads_information(goodreads_source_file, goodreads_info_file)
# filter_goodreads_information(goodreads_info_file)

# add_result_information(goodreads_info_file, goodreads_classification_file)

genre_list = [
    'Architecture',
    'Art',
    'Biography',
    'Business',
    'Economics',
    'Computers',
    'Cooking',
    'Games',
    'Health',
    'History',
    'Languages',
    'Law',
    'Math',
    'Nature',
    'Philosophy',
    'Poetry',
    'Political Science',
    'Psychology',
    'Science',
    'Self Help',
    'Sociology',
    'Sports',
    'Technology',
    'Travel',
    'True Crime',
    'Nonfiction',

    'Drama',
    'Poetry',
    'Fantasy',
    'Humor',
    'Fable',
    'Fairy Tales',
    'Science Fiction',
    'Historical Fiction',
    'Horror',
    'Tall Tale',
    'Legend',
    'Mystery',
    'Romance',
    'Mythology',
    'Fiction in Verse',
    'Young Adult',
    'Fiction'
]

# TODO: Some descriptions are in czech (or some other language)

# Didn't this have issues with the actual extraction?
sample_urls = [
    r'https://www.goodreads.com/list/show/8342.You_Read_a_Book_about_What_',
    r'https://www.goodreads.com/list/show/2122.Medicine_and_Literature',
    r'https://www.goodreads.com/list/show/1058.Microhistory_Social_Histories_of_Just_One_Thing',
    r'https://www.goodreads.com/list/show/692.Best_Science_Books_Non_Fiction_Only',
    r'https://www.goodreads.com/list/show/134.Best_Non_Fiction_no_biographies_',

    # These two have >4000 books on them
    r'https://www.goodreads.com/list/show/281.Best_Memoir_Biography_Autobiography',
    r'https://www.goodreads.com/list/show/101739.Best_of_21st_Century_Non_fiction'
]


# NOTE: I don't need any of this data for the initial prototype (certainly for a more generalized solution)
# The only thing we need to do is extract usable "topical/keyword" information from the book data
# The rest is just mapping stuff onto a knowledge graph (though this is undecided at the moment)
