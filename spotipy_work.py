import os
import spotipy
import psycopg2
import datetime
import time
from artist import Artist
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
from artist_count import artists_of_the_week
from collections import Counter

import json

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.environ['SPOTIPY_CLIENT_ID'],
                                                    client_secret=os.environ['SPOTIPY_CLIENT_SECRET'],
                                                    redirect_uri='https://google.com/',
                                                    scope="user-read-currently-playing"))

connection = psycopg2.connect(user=os.environ['USER'],
                              password=os.environ['PASSWORD'],
                              host=os.environ['HOST'],
                              port=os.environ['PORT'],
                              database=os.environ['DATABASE'])

results = spotify.current_user_playing_track()  # may contain a typeError so CATCH it within code.

print("here we are now ")

max_songs_to_import = int(input("What is the number of songs you want to import? "))

count = 0


# TODO: MAKE the 'get_functions' REUSABLE RATHER THAN JUST ON INITIAL USE.


def import_current_song(artist, song, genre, listened, imported, artist_id,):  # INSERTS TO spotifynstuff database

    if imported:
        check_if_song_skipped(song, imported)
    else:
        try:

            cursor = connection.cursor()
            postgres_insert_query = """INSERT INTO artist (artist_name, song_name, make_date ,listened, genre, 
            artist_id, time_listened) VALUES ( %s, %s, %s, %s, %s, %s, %s) """
            song_listen_time = datetime.datetime.now()
            this_time = datetime.datetime.now()
            current_time = this_time.strftime("%H:%M:%S")
            record_to_insert = (artist, song, song_listen_time, listened, genre, artist_id, current_time)
            cursor.execute(postgres_insert_query, record_to_insert)
            connection.commit()
            print("The artist was inserted")
            imported = True
            global count
            count += 1
            if count == max_songs_to_import:
                print("Shutting down database")
                cursor.close()
                connection.close()
                print("Database closed.")
            else:
                print("Song is already in the current listening track. No need for import. (:")
                check_if_song_skipped(song, imported)

        except (Exception, psycopg2.Error) as error:

            # TODO: IF ERROR =  'NoneType' object is not subscriptable, TRY TO REESTABLISH THE CONNECTION....
            print("Error while connecting to PostgreSQL", error)


def reestablishConnection():
    return


def get_recent_import():
    return


def get_single_artist():
    try:
        artists = results["item"]["artists"]  # gets artist results from the JSON payload
        artist_name = artists[0]["name"]
        print("Artist length is: ", len(artists))
        print(artist_name)
    except TypeError:
        artist_name = ""  # check if this is this is blank

    return artist_name


def get_feature():
    artists = results["item"]["artists"]
    artists_in_song = []
    for i in artists:
        artists_in_song.append(i["name"])

    return len(artists_in_song)


def get_song_name():
    try:
        song_name = results["item"]["name"]
    except TypeError:
        song_name = "no song"
    return song_name


def get_artist_info():
    the_new = Artist(get_single_artist(), get_song_name())  # if no feature
    return the_new


def check_if_song_skipped(song_name, is_imported):
    time_to_fin = 90000  # ms to compare with json payload

    time.sleep(13)
    spotify1 = spotipy.Spotify(
        auth_manager=SpotifyOAuth(client_id=os.environ['SPOTIPY_CLIENT_ID'],  # create a new endpoint everytime
                                  client_secret=os.environ['SPOTIPY_CLIENT_SECRET'],
                                  redirect_uri='https://google.com/',
                                  scope="user-read-currently-playing "
                                        "user-read-playback-state"))

    curr_time = spotify1.current_playback()
    track_playing = spotify1.current_user_playing_track()  # json payload

    curr_song = track_playing["item"]["name"]

    artists = track_playing["item"]["artists"]  # gets artist results from the JSON payload

    this_id = get_artist_id(artists)

    genres = get_genres(this_id)
    print("checking type: ")
    print(type(genres))
    artist_name = artists[0]["name"]
    if song_name != curr_song:
        print("Songs do not match terminating......")
        is_imported = False
        check_if_song_skipped(curr_song, is_imported)

    elif (time_to_fin <= curr_time["progress_ms"]) and (song_name == curr_song):
        print("Checking if song needs to be imported")
        import_current_song(artist_name, curr_song, genres, True, is_imported, this_id)

    else:
        is_imported = False
        print("Song is being listend to \n Needs to import")
        print(curr_time["progress_ms"])
        check_if_song_skipped(song_name, is_imported)


def max_songs():
    num_of_songs = int(input("What is the number of songs you want to import? "))
    return num_of_songs


def check_length_of_artists(artist_list):
    if artist_list >= 2:
        print("Artists length is long")


def get_artist_id(artist_to_get):
    artist_id = artist_to_get[0]["id"]
    return artist_id


def get_genres(artist_id):
    curr_artist = spotify.artist(artist_id)
    genres = curr_artist["genres"]
    return genres


def search_db_artists():
    postgres_insert_query = "SELECT artist_name FROM artist WHERE make_date  BETWEEN NOW()::DATE-EXTRACT(DOW FROM NOW(" \
                            "))::INTEGER-7 AND NOW()::DATE-EXTRACT(DOW from NOW())::INTEGER "
    cursor = connection.cursor()
    cursor.execute(postgres_insert_query)
    value = cursor.fetchall()
    array = []
    counter = 0
    for i in value:
        array.append(i[0])
    array.sort()
    print(array)

    while counter < len(array) - 1:
        curr = array[counter]
        new = ""
        inner_count = 0

        while curr != new:
            if curr == array[counter + 1]:
                print("dupy")
                counter += 1
                inner_count += 1
                artists_of_the_week[curr] = inner_count
            else:
                artists_of_the_week[curr] = inner_count + 1
                new = curr
                print("no")
                counter += 1
                inner_count = 0


def search_genre_of_week():
    postgres_insert_query = "SELECT genre FROM artist WHERE make_date  BETWEEN NOW()::DATE-EXTRACT(DOW FROM NOW(" \
                            "))::INTEGER-7 AND NOW()::DATE-EXTRACT(DOW from NOW())::INTEGER"
    cnt = Counter()
    cursor = connection.cursor()
    cursor.execute(postgres_insert_query)
    value = cursor.fetchall()
    array = []

    for i in value:
        array.append(i[0])  # get the tuple out and make a 2D array

    for index in array:
        for genre in index:
            cnt[genre] += 1

    print(array)
    new_dict = dict(cnt.most_common())
    json_object = json.dumps(new_dict, indent=4)
    return json_object


check_if_song_skipped(get_song_name(), False)
