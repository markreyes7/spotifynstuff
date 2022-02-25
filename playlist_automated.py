import os
import datetime
import spotipy
import psycopg2
from spotipy.oauth2 import SpotifyOAuth
import random
from pprint import pprint

scope = 'playlist-modify-public playlist-modify-private'

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.environ['SPOTIPY_CLIENT_ID'],
                                                    client_secret=os.environ['SPOTIPY_CLIENT_SECRET'],
                                                    redirect_uri='https://google.com/',
                                                    scope=scope))

connection = psycopg2.connect(user=os.environ['USER'],
                              password=os.environ['PASSWORD'],
                              host=os.environ['HOST'],
                              port=os.environ['PORT'],
                              database=os.environ['DATABASE'])
print("Cursor is opening.......")
cursor = connection.cursor()

print("Cursor is now opened.")


# TODO: ADD THE NEW SONG TO DB, BUT WITH LISTENED TO BE MARKED AS FALSE.


def get_random_id_from_db():
    sql_SELECT_QUERY = "SELECT artist_id FROM artist ORDER BY RANDOM() LIMIT 1;"

    cursor.execute(sql_SELECT_QUERY)
    x = cursor.fetchone()[0]
    return x


def get_random_album_id(artist_id):
    all_albums = spotify.artist_albums(artist_id, limit=25)
    length_of_all_albums = len(all_albums["items"])
    position = all_albums['items'][random.randint(0, length_of_all_albums - 1)]  # generates a random album
    album_id = position["id"]
    return album_id


def get_random_song(album_id):
    current_tracks = spotify.album_tracks(album_id)
    total_tracks = len(current_tracks["items"])
    pos = current_tracks['items'][random.randint(0, total_tracks - 1)]
    song_name = pos['name']
    song_uri = pos['uri']
    return song_name, song_uri,


# TODO:Instead of iterating through array of existing songs in DB, use IDs to find the position of the song.


def import_random_song():
    song_import = False
    id_from_db = get_random_id_from_db()
    album_id = get_random_album_id(id_from_db)
    song_tuple = get_random_song(album_id)
    song_name = song_tuple[0]
    song_id = song_tuple[1]

    print(song_name)
    cursor.execute("""SELECT song_name FROM artist WHERE artist_id = %s """, (id_from_db,))
    for record in cursor:
        if song_name == record[0]:
            print("Matching songs")
            import_random_song()
            break
        else:
            print("no match. \n Adding to the playlist")
            song_import = True
        print(record[0] + " is our current song")
    cursor.close()
    connection.close()
    if song_import:
        spotify.playlist_add_items(os.environ['PLAYLIST_ID'], [song_id])


def delete_from_playlist():
    curr_playlist = spotify.playlist_items(os.environ['PLAYLIST_ID'])
    items = curr_playlist['items']

    for count, value in enumerate(items):
        pprint("Song no." + str(count + 1) + " " + items[count]['track']['name'] + " ")

    to_delete = int(input("What would you like to delete: "))
    track = items[to_delete - 1]['track']
    song_to_remove = track['uri']

    spotify.playlist_remove_specific_occurrences_of_items(os.environ['PLAYLIST_ID'],
                                                          [{"uri": song_to_remove, "positions": [to_delete - 1]}])
    import_deleted_to_db(track)


def get_genres(artist_id):
    curr_artist = spotify.artist(artist_id)
    genres = curr_artist["genres"]
    return genres


def import_deleted_to_db(track):
    postgres_insert_query = """INSERT INTO artist (artist_name, song_name, make_date ,listened, genre, artist_id) VALUES (
                %s, %s, %s, %s, %s, %s) """
    song_listen_time = datetime.datetime.now()
    artist_name = track['artists'][0]['name']
    print("name is " + artist_name)
    artist_id = track['artists'][0]['id']
    print("id is " + artist_id)
    genres = get_genres(artist_id)
    song_name = track['name']
    print("song was " + song_name)
    record_to_insert = (artist_name, song_name, song_listen_time, True, genres, artist_id)
    cursor.execute(postgres_insert_query, record_to_insert)
    connection.commit()
    print("The artist was inserted")
    connection.close()


print(5/2)
