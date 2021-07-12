class ArtistWithFeature: # for multiple artists on one track.
    def __init__(self, artist, featuring, song_name):
        self.artist = artist
        self.featuring = featuring  # will be array
        self.song_name = song_name
