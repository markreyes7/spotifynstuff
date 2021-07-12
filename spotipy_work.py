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

results = spotify.current_user_playing_track()


def import_current_song(artist,song):  # INSERTS TO spotifynstuff database
    try:
        connection = psycopg2.connect(user=os.environ['USER'],
                                      password=os.environ['PASSWORD'],
                                      host=os.environ['HOST'],
                                      port=os.environ['PORT'],
                                      database=os.environ['DATABASE'])

        cursor = connection.cursor()
        postgres_insert_query = """INSERT INTO artist (artist_name, song_name, make_date ,listened) VALUES (%s, %s, 
        %s, %s) """
        song_listen_time = datetime.datetime.now()
        record_to_insert = (artist, song, song_listen_time, True)
        cursor.execute(postgres_insert_query, record_to_insert)
        connection.commit()
        print("The artist was inserted")

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


def get_single_artist():
    artists = results["item"]["artists"]  # gets artist results from the JSON payload
    artist_name = artists[0]["name"]

    print("Artist length is: ", len(artists))
    print(artist_name)
    return artist_name


def get_feature():
    artists = results["item"]["artists"]
    artists_in_song = []
    for i in artists:
        artists_in_song.append(i["name"])


def get_song_name():
    song_name = results["item"]["name"]
    return song_name


def get_artist_info():
    the_new = Artist(get_single_artist(), get_song_name())  # if no feature
    return the_new


get_single_artist()


def check_if_song_skipped(song_name):
    is_curr = True

    time_to_fin = 90000    # ms to compare with json payload

    time.sleep(13)
    spotify1 = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.environ['SPOTIPY_CLIENT_ID'],   # create a new endpoint everytime
                                                          client_secret=os.environ['SPOTIPY_CLIENT_SECRET'],
                                                          redirect_uri='https://google.com/',
                                                          scope="user-read-currently-playing "
                                                                "user-read-playback-state"))

    curr_time = spotify1.current_playback()
    results1 = spotify1.current_user_playing_track()  # json payload

    curr_song = results1["item"]["name"]

    artists = results1["item"]["artists"]  # gets artist results from the JSON payload
    artist_name = artists[0]["name"]
    if song_name != results1["item"]["name"]:
        print("Songs do not match terminating......")
        check_if_song_skipped(curr_song)

    elif (time_to_fin <= curr_time["progress_ms"]) and (song_name == results1["item"]["name"]):
        print("songs are are ready to import")
        import_current_song(artist_name, curr_song)

    else:
        print("Song is being listend to \n Needs to import")
        print(curr_time["progress_ms"])
        check_if_song_skipped(song_name)



check_if_song_skipped(get_song_name())
