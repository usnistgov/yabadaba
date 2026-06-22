from yabadaba.record import Record

import pandas as pd
class Track(Record):

    ########################## Basic metadata fields ##########################

    @property
    def style(self):
        """str: The record style"""
        return 'track'

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return 'track'
    
    ############################# Define Values  ##############################

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """
        self._add_value('str', 'title', description='track title')
        self._add_value('int', 'number', description='track number')
        self._add_value('time_delta', 'duration')
        self._add_value('longstr', 'lyrics')

class Album(Record):
    """
    Class for representing a music album.
    """

    ########################## Basic metadata fields ##########################

    @property
    def style(self):
        """str: The record style"""
        return 'album'

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return 'album'
    

    ############################# Define Values  ##############################

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """
        self._add_value('longstr', 'artist', description='artist name')
        self._add_value('str', 'producer', description='producer name')
        self._add_value('str', 'album', description='album title')
        self._add_value('date', 'releasedate', description='release date')
        self._add_value('strlist', 'genre')

        self._add_value('recordlist', 'tracks', recordclass=Track, description='List of album tracks')

        # Modify tracks queries
        self.get_value('tracks').queries.pop('number')
        
    def add_track(self, **kwargs):
        """Adds a new track to the tracks list"""
        self.get_value('tracks').append(**kwargs)

    def tracks_metadata(self) -> pd.DataFrame:
        """Compiles the tracks metadata for this album into a pandas.DataFrame"""
        df = []
        for track in self.tracks:
            df.append(track.metadata())
        df = pd.DataFrame(df)
        return df