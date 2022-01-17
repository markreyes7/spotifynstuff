import os
import spotipy
import psycopg2
import datetime
import time
from artist import Artist
from spotipy.oauth2 import SpotifyOAuth

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

value = ""

count = 0


def import_current_song(artist, song, genre, imported):  # INSERTS TO spotifynstuff database

    if imported:
        check_if_song_skipped(song, imported)
    else:
        try:
            cursor = connection.cursor()
            postgres_insert_query = """INSERT INTO artist (artist_name, song_name, make_date ,listened, genre) VALUES (
            %s, %s, %s, %s, %s) """
            song_listen_time = datetime.datetime.now()
            record_to_insert = (artist, song, song_listen_time, True, genre)
            cursor.execute(postgres_insert_query, record_to_insert)
            connection.commit()
            print("The artist was inserted")
            imported = True
            global count
            count += 1
            if count == 5:
                cursor.close()
                connection.close()
                print("posty closed.")
            else:
                check_if_song_skipped(song, imported)

        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)




# finally:
#     if connection:
#         cursor.close()
#         connection.close()
#         print("PostgreSQL connection is closed")


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

    time.sleep(13)  # wait 13 before next request
    spotify1 = spotipy.Spotify(
        auth_manager=SpotifyOAuth(client_id=os.environ['SPOTIPY_CLIENT_ID'],  # create a new endpoint everytime
                                  client_secret=os.environ['SPOTIPY_CLIENT_SECRET'],
                                  redirect_uri='https://google.com/',
                                  scope="user-read-currently-playing "
                                        "user-read-playback-state"))

    curr_time = spotify1.current_playback()
    results1 = spotify1.current_user_playing_track()  # json payload

    curr_song = results1["item"]["name"]

    artists = results1["item"]["artists"]  # gets artist results from the JSON payload

    this_id = get_artist_id(artists)

    genres = get_genres(this_id)
    print("checking type: ")
    print(type(genres))
    artist_name = artists[0]["name"]
    if song_name != results1["item"]["name"]:
        print("Songs do not match terminating......")
        is_imported = False
        check_if_song_skipped(curr_song, is_imported)

    elif (time_to_fin <= curr_time["progress_ms"]) and (song_name == results1["item"]["name"]):
        print("songs are are ready to import")
        import_current_song(artist_name, curr_song, genres, is_imported)

    else:
        is_imported = False
        print("Song is being listend to \n Needs to import")
        print(curr_time["progress_ms"])
        check_if_song_skipped(song_name, is_imported)


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


# TODO: Keep the program running after import is made.
#   Checking if the song is skipped
#   - IF SONG IS SKIPPED THEN BEGIN NEXT IMPORT CHECKING MODE.
#   - IF THE SONG IS STILL PLAYING WAIT UNTIL IT I


check_if_song_skipped(get_song_name(), False)
