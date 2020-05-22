import requests
from pandas.io.json import json_normalize
import json
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import pandas as pd

from tqdm import tqdm

import itertools
import argparse


def perf_clock(func):
    
    """
    calculate total time taken
    
    params : func
    
    return : wrapper
    """
    
    def perf_clocked(*args):
        # start
        st = time.perf_counter()
        result = func(*args)
        
        # end
        et = time.perf_counter() - st

        # argument -> outputpath
        path = args[0]
        
        # name of function
        name = func.__name__

        print('site name : %s \ntotal time : [%0.5fs] \noutput path : %s' % (name, et, path))

        return result

    return perf_clocked

@perf_clock
def tubi_crawling(output_path):
    """
    crawls tubi_id, title, release date, genre, director, actor, country, poster_url from tubi movie streaming site.
    
    receives json file from tubi site.
    
    average total time : 1061s
    
    creates excel file at output_path
    
    """
    
    # get Categories
    hash_json = requests.get("https://tubitv.com/oz/containers?expand=0").json()['hash'] # get hash values
    
    # all genres tags list
    genres_tags = []

    # get tags with 'Genres' in its tags
    for genre in hash_json:

        tags = hash_json[genre]['tags']

        if 'Genres' in tags:
            genres_tags.append(genre)

    # sort
    genres_tags.sort()
    
    to_delete_list = ['sports_movies_and_tv', 'crime_tv', 'docuseries', 'foreign_language_tv', 'kids_shows', 'para_los_nios_y_familias', 'preschool', 'reality_tv', 'telenovelas_y_series', 'tv_comedies', 'tv_dramas', 'lifestyle_tv']

    genres_tags = list(set(genres_tags) - set(to_delete_list))
    
    # create dataframe
    tubi_df = pd.DataFrame(columns = ['tubi_id', 'title', 'release', 'genre','director', 'actor', 'country', 'runtime', 'production', 'overview','url', 'image_url'])
    
    row_list = []
    
    for tag in tqdm(genres_tags):

        try:
            s = requests.Session()
            
            req = s.get('https://tubitv.com/oz/containers/{}/content?parentId&cursor=0&limit={}&isKidsModeEnabled=false'.format(tag, 100000)).json()

            # print(tag + " pages Started!")
            
            movie_ids = list(req['contents'].keys())

            for i, tubi_id in enumerate(movie_ids):

                try:
                    
                    if req['contents'][tubi_id]['type'] == 's':
                        # print(req['contents'][tubi_id])
                        pass
                    
                    else:
                        try:
                            title = req['contents'][tubi_id]['title'] # title 값
                        except:
                            title = None

                        try:
                            release = req['contents'][tubi_id]['year'] # year 값
                        except:
                            release = None

                        
                        # director
                        try: 
                            director_temp = req['contents'][tubi_id]['directors'] # directors 값
                            director = ""

                            for i,temp in enumerate(director_temp):
                                if i == 0:
                                    director += temp
                                else:
                                    genre += ',' + temp

                        except:
                            director = None
                            
        
                        title_url = title.lower().replace(" ", '_') # title_url용으로 바꾸기 
                        url = 'https://tubitv.com/movies/{}/{}'.format(tubi_id, title_url) # url 값 설정
                        
                        # actor
                        try:
                            actor_temp = req['contents'][tubi_id]['actors'] # actors
                            actor = ''

                            for i,temp in enumerate(actor_temp):
                                if i == 0:
                                    actor += temp
                                else:
                                    actor += ',' + temp
                        except:
                            actor = None
                            
                        # genre
                        try:
                            genre_temp = req['contents'][tubi_id]['tags']

                            genre = ''

                            for i,temp in enumerate(genre_temp):
                                if i == 0:
                                    genre += temp
                                else:
                                    genre += ',' + temp
                        except:
                            genre = None
                        
                        # overview
                        try:
                            overview = req['contents'][tubi_id]['description']
                        except:
                            overview = None
                        
                        # runtime
                        try:
                            runtime = int(int(req['contents'][tubi_id]['duration']) / 60)
                        except:
                            runtime = None
                        
                        # poster url
                        try:
                            poster_url = req['contents'][tubi_id]['posterarts'][0]
                            
                        except:
                            poster_url = None
                        
                        
                        row_list.append([tubi_id, title, release,genre, director,actor,None,runtime,None,overview, url, poster_url])
                        
                        # print(list(row_list))
                        
                        # print(row_list[-1])
                        # row_list.append([tubi_id, title, release,genre, director,actor,None,runtime,None,overview, url, poster_url]) # df 에 추가
                        # print(row_list[-1])
                except:
                    pass
                    # row_list.append([None for _ in range(len(tubi_df.columns))])
                    # print(row_list[-1])
        except:
            print("Not Working")
            pass    
    
    # put in tubi_df
    for i, row in tqdm(enumerate(row_list)):
        tubi_df.loc[i] = row
    
    tubi_df.drop_duplicates(inplace=True)
    
    with pd.ExcelWriter(output_path, engine='xlsxwriter', options={'strings_to_urls' : False}) as writer:
        tubi_df.to_excel(writer)

if __name__ == "__main__":
    # create the parser
    
    my_parser = argparse.ArgumentParser(description='Vudu site Crawler')

    my_parser.add_argument('output_path',
                       metavar='output_path',
                       type=str,
                       help='output_path for excel file')

    args = my_parser.parse_args()

    output_path = args.output_path

    tubi_crawling(output_path)
