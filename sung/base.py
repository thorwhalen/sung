"""Base functionalities for the sung package."""

from typing import Callable
from operator import itemgetter
from sung.util import (
    get_spotify_client,
    ensure_client,
    DFLT_LIMIT,
    extractor,
    cast_track_key,
)


# TODO: Include all modifiers in the signature (only year and genre for now)?
# TODO: Make signature using Spotify.search signature
def search_tracks(
    query: str,
    egress: Callable = extractor('tracks.items'),
    *,
    search_type='track',
    market=None,
    year=None,
    genre=None,
    limit: int = DFLT_LIMIT,
    offset: int = 0,
    client=get_spotify_client,
):
    """
    Search for tracks on Spotify.

    Parameters:
        - query - the search query (see how to write a query in the
                official documentation https://developer.spotify.com/documentation/web-api/reference/search/)  # noqa
        - search_type - the types of items to return. One or more of 'artist', 'album',
                    'track', 'playlist', 'show', and 'episode'.  If multiple types are desired,
                    pass in a comma separated string; e.g., 'track,album,episode'.
        - market - An ISO 3166-1 alpha-2 country code or the string
                    from_token.
        - limit - the number of items to return (min = 1, default = 10, max = 50). The limit is applied
                    within each type, not on the total response.
        - offset - the index of the first item to return

    """
    client = ensure_client(client)

    # Build query
    # TODO: Make function using spotify_search_modifiers to do this
    query_string = query
    if year:
        query_string += f" year:{year}"
    if genre:
        query_string += f" genre:{genre}"

    # Execute search
    results = client.search(
        q=query_string, type=search_type, market=market, limit=limit, offset=offset
    )

    # Extract tracks and return a list of song names with additional details

    return egress(results)


class Playlist:
    """A Spotify playlist."""

    def __init__(self, playlist_id):
        self.sp = get_spotify_client(
            scope="playlist-modify-private playlist-modify-public"
        )
        self.playlist_id = playlist_id

    def __repr__(self):
        return f'Playlist("{self.playlist_id}")'

    @classmethod
    def create_from_track_list(
        cls, track_list=(), playlist_name="New Playlist", public=True
    ):
        """
        Create a new playlist from a list of track IDs.
        """

        track_list = [cast_track_key(track, "uri") for track in track_list]

        if public is False:
            raise NotImplemented("Private playlists are not yet supported")

        scope = "playlist-modify-private playlist-modify-public"

        sp = get_spotify_client(scope=scope)

        # Get the current user's ID
        user_id = sp.me()['id']

        # Create a new playlist
        playlist = sp.user_playlist_create(
            user=user_id, name=playlist_name, public=public
        )
        playlist_id = playlist['id']

        # Add tracks to the playlist in batches of 100
        for i in range(0, len(track_list), 100):
            sp.playlist_add_items(playlist_id, track_list[i : i + 100])

        return cls(playlist_id)

    def add_songs(self, track_list):
        if isinstance(track_list, str):
            track_list = [track_list]
        for i in range(0, len(track_list), 100):
            self.sp.playlist_add_items(self.playlist_id, track_list[i : i + 100])

    def delete_songs(self, track_list):
        if isinstance(track_list, str):
            track_list = [track_list]
        self.sp.playlist_remove_all_occurrences_of_items(self.playlist_id, track_list)


track_spec = {
    'name': 'name',
    'artist': ('artists', [0, 'name']),
    'album': 'album.name',
    'release_date': 'album.release_date',
    'duration_ms': 'duration_ms',
    'popularity': 'popularity',
    'explicit': 'explicit',
    'external_url': 'external_urls.spotify',
    'preview_url': 'preview_url',
    'track_number': 'track_number',
    'album_total_tracks': 'album.total_tracks',
    'available_markets': 'available_markets',
    'album_images': 'album.images',
}


def track_metadata(track_id, *, client=get_spotify_client):
    client = ensure_client(client)

    # Get track details
    track = client.track(track_id)

    # Prepare metadata dictionary
    metadata = {
        'name': track['name'],
        'artist': track['artists'][0]['name'],
        'album': track['album']['name'],
        'release_date': track['album']['release_date'],
        'duration_ms': track['duration_ms'],
        'popularity': track['popularity'],
        'explicit': track['explicit'],
        'external_url': track['external_urls']['spotify'],
        'preview_url': track['preview_url'],  # 30s preview if available
        'track_number': track['track_number'],
        'album_total_tracks': track['album']['total_tracks'],
        'available_markets': track['available_markets'],
        'album_images': track['album']['images'],
    }

    return metadata
