"""Utility functions for the sung package."""

# TODO: use openAPI definition to create pydantic models for data
#  see https://github.com/thorwhalen/sung/discussions/1#discussioncomment-10990012


import re
import os
from datetime import datetime
from typing import (
    Literal,
    T,
    Callable,
    TypeVar,
    Optional,
    Dict,
    Union,
    Iterable,
    Any,
    Mapping,
)
from functools import partial

from glom import glom, Spec, Coalesce
import pandas as pd
from i2 import Sig


from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth


DFLT_LIMIT = 20

# TODO: Get automatically from pydantic model when available
SearchTypeT = Literal["artist", "album", "track", "playlist", "show", "episode"]


def identity(x: T) -> T:
    return x


def strip_values(d: dict) -> dict:
    """Return a new dictionary with all string values stripped."""
    return {k: v.strip() for k, v in d.items()}


Extractor = TypeVar("Extractor", bound=Callable)  # TODO: Specify more precisely


SpecT = Union[Spec, str, Iterable[str], Mapping[str, str]]


def extractor(spec: SpecT) -> Extractor:
    if isinstance(spec, str):
        return partial(glom, spec=spec, default=None)
    elif isinstance(spec, Iterable) and not isinstance(spec, Mapping):
        spec = {k: k for k in spec}
    return partial(glom, spec=coalesce_to_default(spec))


def df_extraction(extractor_func, df) -> Extractor:
    t = df.apply(extractor_func, axis=1)
    return pd.DataFrame(list(t.values), index=t.index)


def df_extractor(spec: SpecT) -> pd.DataFrame:
    return partial(df_extraction, extractor(spec))


def is_extractor(x: Any) -> bool:
    return (
        callable(x)
        and hasattr(x, "func")
        and getattr(x.func, "__name__", "") == "glom"
        or x is identity
    )


def ensure_extractor(x: Any) -> Extractor:
    if x is None:
        return identity
    if is_extractor(x):
        return x
    else:
        return extractor(x)


extractor.is_extractor = is_extractor
extractor.ensure_extractor = ensure_extractor


def coalesce_string_values(d: dict, **coalece_kwargs) -> dict:
    def coalesced_items():
        for k, v in d.items():
            if isinstance(v, str):
                yield k, Coalesce(v, **coalece_kwargs)
            else:
                yield k, v

    return dict(coalesced_items())


coalesce_to_default = partial(coalesce_string_values, default=None)


def convert_date(date_str: str, read_formats=("%Y-%m-%d", "%Y", "%Y-%m")):
    """Convert a date string to a standard format (YYYY-MM-DD)."""
    if date_str is None:
        return None
    for fmt in read_formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return date_str


def get_config(config_name: str) -> str:
    """Get the value of a configuration variable."""
    if config_name in os.environ:
        return os.environ[config_name]
    else:
        raise ValueError(
            f"Configuration variable {config_name} not found. "
            "Please set it in the environment. To get your Spotify API credentials, "
            "see https://developer.spotify.com/documentation/web-api/tutorials/getting-started"
        )


def pop_client_id_and_secret(kwargs) -> tuple[str, str]:
    client_id = kwargs.pop("client_id", get_config("SPOTIFY_API_CLIENT_ID"))
    client_secret = kwargs.pop("client_secret", get_config("SPOTIFY_API_CLIENT_SECRET"))
    return client_id, client_secret


def get_spotify_creds(**client_creds_kwargs) -> SpotifyClientCredentials:
    client_id, client_secret = pop_client_id_and_secret(client_creds_kwargs)
    return SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret,
        **client_creds_kwargs,
    )


def get_spotify_oauth_creds(**oauth_kwargs) -> SpotifyOAuth:
    client_id, client_secret = pop_client_id_and_secret(oauth_kwargs)
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        **oauth_kwargs,
    )


def _extract_scope_items(scope_string: str) -> Iterable[str]:
    if isinstance(scope_string, str):
        return re.findall("\S+", scope_string)
    else:
        assert isinstance(scope_string, Iterable)
        return scope_string


def _add_to_scope(scope, more_scope=""):
    """
    Add new_scope to scope, ensuring no duplicates.

    Examples:

    >>> _add_to_scope('user-top-read', 'user-read-recently-played')  # note the lexicographic order in output
    'user-read-recently-played user-top-read'
    >>> _add_to_scope('user-top-read', 'user-read-recently-played user-top-read')  # note the absence of duplicates in output
    'user-read-recently-played user-top-read'
    """
    scope_items = set(_extract_scope_items(scope))
    scope_items.update(_extract_scope_items(more_scope))
    return " ".join(sorted(scope_items))


# def get_spotify_client(client=None, *, ensure_scope=None, **kwargs) -> Spotify:
#     if ensure_scope is not None:
#         kwargs['scope'] = _add_to_scope(kwargs.get('scope', ''), ensure_scope)

#     spotify_kwargs = Sig(Spotify).map_arguments(
#         kwargs=kwargs, allow_partial=True, allow_excess=True
#     )
#     client_creds_kwargs = Sig(SpotifyClientCredentials).map_arguments(
#         kwargs=kwargs, allow_partial=True, allow_excess=True
#     )

#     if client is None:
#         return Spotify(
#             auth_manager=get_spotify_creds(**client_creds_kwargs),
#             **spotify_kwargs,
#         )
#     else:
#         # make a new client, with the updated kwargs
#         # extract the client_creds_kwargs and spotify_kwargs kwargs from client instance
#         # and update them with the new kwargs
#         # then create a new client with these updated kwargs
#         # return the new client

from i2 import Sig


spotify_client_sig = (
    Sig(Spotify)
    .merge_with_sig(Sig(SpotifyOAuth) - "requests_timeout")
    .merge_with_sig(Sig(SpotifyClientCredentials) - "requests_timeout")
)


@spotify_client_sig.inject_into_keyword_variadic
def get_spotify_client(client=None, *, ensure_scope="", scope="", **kwargs) -> Spotify:
    """
    Get a Spotify client.

    Parameters:
        - client - an existing Spotify client (optional)
        - ensure_scope - a scope to ensure is included in the client's auth_manager (optional)
        - scope - the scope to use for the client (optional)
        - **kwargs - additional arguments to pass to the Spotify client

    The purpose of having scope and ensure_scope is to allow you to ensure some needed
    scopes exist when a code block is asking for a Spotify client with it's own
    scope desires.

    """
    scope = _add_to_scope(kwargs.get("scope", ""), ensure_scope)
    kwargs["scope"] = scope

    spotify_kwargs = Sig(Spotify).map_arguments(
        kwargs=kwargs, allow_partial=True, allow_excess=True
    )

    if scope:
        client_creds_kwargs = Sig(SpotifyOAuth).map_arguments(
            kwargs=kwargs, allow_partial=True, allow_excess=True
        )
    else:
        client_creds_kwargs = Sig(SpotifyClientCredentials).map_arguments(
            kwargs=kwargs, allow_partial=True, allow_excess=True
        )

    if client is None:
        return Spotify(
            auth_manager=get_spotify_oauth_creds(**client_creds_kwargs),
            **spotify_kwargs,
        )
    else:
        # TODO: Should I use glom extractors here?
        # Extract existing spotify_kwargs from the client instance

        existing_spotify_kwargs = {
            "proxies": client.proxies,
            "requests_timeout": client.requests_timeout,
            "status_forcelist": client.status_forcelist,
            "retries": client.retries,
            "status_retries": client.status_retries,
            "backoff_factor": client.backoff_factor,
            "language": client.language,
            # 'chunked': client.chunked,
        }

        # Update existing spotify_kwargs with new spotify_kwargs
        spotify_kwargs = {**existing_spotify_kwargs, **spotify_kwargs}

        # Extract existing client_creds_kwargs from client.auth_manager
        existing_client_creds_kwargs = {}
        auth_manager = client.auth_manager

        if isinstance(auth_manager, SpotifyClientCredentials):
            existing_client_creds_kwargs = {
                "client_id": auth_manager.client_id,
                "client_secret": auth_manager.client_secret,
                "proxies": auth_manager.proxies,
                "requests_timeout": auth_manager.requests_timeout,
            }
        elif isinstance(auth_manager, SpotifyOAuth):
            existing_client_creds_kwargs = {
                "client_id": auth_manager.client_id,
                "client_secret": auth_manager.client_secret,
                "proxies": auth_manager.proxies,
                "requests_timeout": auth_manager.requests_timeout,
                "redirect_uri": auth_manager.redirect_uri,
                "scope": auth_manager.scope,
            }
        elif hasattr(auth_manager, "client_id") and hasattr(
            auth_manager, "client_secret"
        ):
            # For other auth managers that have client_id and client_secret
            existing_client_creds_kwargs = {
                "client_id": auth_manager.client_id,
                "client_secret": auth_manager.client_secret,
            }

        # Update existing client_creds_kwargs with new client_creds_kwargs
        client_creds_kwargs = {**existing_client_creds_kwargs, **client_creds_kwargs}

        # Create a new auth_manager with the updated client_creds_kwargs
        new_auth_manager = get_spotify_creds(**client_creds_kwargs)

        # Create a new Spotify client with the updated kwargs
        return Spotify(
            auth_manager=new_auth_manager,
            **spotify_kwargs,
        )


spotify_search_modifiers = {
    "album:": "Search within album titles.",
    "artist:": "Search within artist names.",
    "genre:": "Restrict search results to a specific genre. Example: genre:jazz.",
    "track:": "Search within track names.",
    "year:": "Filter by release year. Accepts ranges (e.g., year:2000-2020).",
    "tag:new": "Search for newly released songs.",
    "tag:hipster": "Search for music outside the mainstream (less popular).",
    "isrc:": "Search using the International Standard Recording Code.",
    "upc:": "Search using the Universal Product Code.",
}

spotify_scopes = {
    "ugc-image-upload": "Write access to user-provided images.",
    "user-read-playback-state": "Read access to a user’s player state.",
    "user-modify-playback-state": "Write access to a user’s playback state.",
    "user-read-currently-playing": "Read access to a user’s currently playing content.",
    "app-remote-control": "Remote control playback of Spotify (SDK use only).",
    "streaming": "Control playback of a Spotify track (requires Premium).",
    "playlist-read-private": "Read access to user's private playlists.",
    "playlist-read-collaborative": "Read access to collaborative playlists.",
    "playlist-modify-private": "Write access to user's private playlists.",
    "playlist-modify-public": "Write access to user's public playlists.",
    "user-follow-modify": "Write/delete access to user's followed artists and users.",
    "user-follow-read": "Read access to user's followed artists and users.",
    "user-read-playback-position": "Read access to user's playback position.",
    "user-top-read": "Read access to user's top artists and tracks.",
    "user-read-recently-played": "Read access to user's recently played tracks.",
    "user-library-modify": "Write/delete access to user's 'Your Music' library.",
    "user-library-read": "Read access to user's library.",
    "user-read-email": "Read access to user's email address.",
    "user-read-private": "Read access to user's subscription details.",
    "user-soa-link": "Link a partner user account to a Spotify user account.",
    "user-soa-unlink": "Unlink a partner user account from a Spotify account.",
    "soa-manage-entitlements": "Modify entitlements for linked users.",
    "soa-manage-partner": "Update partner information.",
    "soa-create-partner": "Create new partners (platform partners only).",
}


# TODO: Verify: Doesn't seem all correct. Perhaps get from pydantic model?
spotify_track_metadata_fields = {
    "name": "The name of the track.",
    "artists": "Artists associated with the track.",
    "album": "Information about the album in which the track appears.",
    "release_date": "The release date of the album or single. Format can vary (e.g., YYYY-MM-DD).",
    "duration_ms": "The track's duration in milliseconds.",
    "popularity": "The popularity of the track, with values ranging from 0 to 100. Higher values indicate greater popularity.",
    "explicit": "A boolean indicating whether the track contains explicit content.",
    "external_url": "A dictionary of external URLs, including a link to the track on Spotify.",
    "preview_url": "A URL to a 30-second preview of the track, if available.",
    "track_number": "The track's position within its album or single. The first track is 1.",
    "album_total_tracks": "The total number of tracks in the album that contains this track.",
    "available_markets": "A list of country codes where the track is available.",
    "album_images": "A list of album cover art images in various sizes, with URLs to access them.",
    "album_release_year": "The year in which the album was released.",
}

# TODO: Replace spotify_track_metadata_fields with one generated by ju.model_field_descriptions, and add
#   standard_track_metadata to make an extended version, or extend spotify_track_metadata_fields itself
# # spotify_track_metadata_fields = strip_values(__import__('ju').model_field_descriptions(TrackObject))
# spotify_track_metadata_fields = {'artists': 'The artists who performed the track. Each artist object includes a link in `href` to more detailed information about the artist.',
#  'available_markets': 'A list of the countries in which the track can be played, identified by their [ISO 3166-1 alpha-2](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code.',
#  'disc_number': 'The disc number (usually `1` unless the album consists of more than one disc).',
#  'duration_ms': 'The track length in milliseconds.',
#  'explicit': 'Whether or not the track has explicit lyrics ( `true` = yes it does; `false` = no it does not OR unknown).',
#  'external_urls': 'External URLs for this track.',
#  'href': 'A link to the Web API endpoint providing full details of the track.',
#  'id': 'The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) for the track.',
#  'is_playable': 'Part of the response when [Track Relinking](/documentation/web-api/concepts/track-relinking/) is applied. If `true`, the track is playable in the given market. Otherwise `false`.',
#  'linked_from': 'Part of the response when [Track Relinking](/documentation/web-api/concepts/track-relinking/) is applied and is only part of the response if the track linking, in fact, exists. The requested track has been replaced with a different track. The track in the `linked_from` object contains information about the originally requested track.',
#  'restrictions': 'Included in the response when a content restriction is applied.',
#  'name': 'The name of the track.',
#  'preview_url': 'A URL to a 30 second preview (MP3 format) of the track.',
#  'track_number': 'The number of the track. If an album has several discs, the track number is the number on the specified disc.',
#  'type': 'The object type: "track".',
#  'uri': 'The [Spotify URI](/documentation/web-api/concepts/spotify-uris-ids) for the track.',
#  'is_local': 'Whether or not the track is from a local file.'}

spotify_track_metadata_description = (
    spotify_track_metadata_fields  # backcompatibility alias
)

spotify_track_metadata_numerical_field_names = [
    "duration_ms",
    "popularity",
    "explicit",
    "album_release_year",
]

spotify_album_metadata_fields_names = [
    "available_markets",
    "type",
    "album_type",
    "href",
    "id",
    "images",
    "name",
    "release_date",
    "release_date_precision",
    "uri",
    "artists",
    "external_urls",
    "total_tracks",
]


spotify_album_metadata_fields = {
    "available_markets": "A list of country codes where the album is available.",
    "album_type": "The type of the album: 'album', 'single', 'compilation', etc.",
    "href": "A link to the Web API endpoint providing full details of the album.",
    "id": "The Spotify ID for the album.",
    "images": "A list of album cover art images in various sizes, with URLs to access them.",
    "name": "The name of the album.",
    "release_date": "The release date of the album. Format can vary (e.g., YYYY-MM-DD).",
    "release_date_precision": "The precision of the release date: 'year', 'month', or 'day'.",
    "uri": "The Spotify URI for the album.",
    "artists": "Artists associated with the album.",
    "external_urls": "A dictionary of external URLs, including a link to the album on Spotify.",
    "total_tracks": "The total number of tracks in the album.",
}


spotify_audio_features_fields = {
    "acousticness": "A confidence measure from 0.0 to 1.0 indicating the likelihood that the track is acoustic. Higher values denote a higher probability. Range: 0.0 to 1.0.",
    "danceability": "Reflects how suitable a track is for dancing, based on tempo, rhythm stability, beat strength, and overall regularity. Higher values indicate greater danceability. Range: 0.0 to 1.0.",
    "energy": "Measures the intensity and activity of a track. Energetic tracks feel fast, loud, and noisy. Higher values represent more energy. Range: 0.0 to 1.0.",
    "instrumentalness": "Predicts whether a track contains no vocals. Higher values suggest a greater likelihood of the track being instrumental. Range: 0.0 to 1.0.",
    "liveness": "Detects the presence of an audience in the recording. Higher values indicate a higher probability of the track being performed live. Range: 0.0 to 1.0.",
    "loudness": "The overall loudness of a track in decibels (dB), averaged across the entire track. Useful for comparing the relative loudness of tracks. Typical range: -60 to 0 dB.",
    "speechiness": "Measures the presence of spoken words in a track. Higher values indicate more speech-like content. Values above 0.66 suggest tracks made entirely of spoken words; values between 0.33 and 0.66 may contain both music and speech; values below 0.33 likely represent music and other non-speech-like tracks. Range: 0.0 to 1.0.",
    "valence": "Describes the musical positiveness conveyed by a track. Higher values sound more positive (e.g., happy, cheerful), while lower values sound more negative (e.g., sad, angry). Range: 0.0 to 1.0.",
    "tempo": "The estimated tempo of a track in beats per minute (BPM). Range: 0 to 250 BPM.",
    "key": "The estimated overall key of the track, represented as an integer corresponding to standard Pitch Class notation (e.g., 0 = C, 1 = C♯/D♭, ..., 11 = B). If no key was detected, the value is -1. Range: -1 to 11.",
    "mode": "Indicates the modality (major or minor) of a track. Major is represented by 1 and minor by 0. Range: 0 or 1.",
    "time_signature": "An estimated overall time signature of a track, indicating how many beats are in each bar. Range: 3 to 7.",
}

spotify_features_fields = dict(
    **{
        k: spotify_track_metadata_fields[k]
        for k in spotify_track_metadata_numerical_field_names
    },
    **spotify_audio_features_fields,
)

spotify_features_field_names = tuple(spotify_features_fields) + (
    "album_release_year",
    "explicit",
)

# TODO: When supporting only 3.11+, use Literal[*spotify_features_field_names]
SpotifyFeaturesT = Literal[
    "duration_ms",
    "popularity",
    "album_release_year",
    "explicit",
    "acousticness",
    "danceability",
    "energy",
    "instrumentalness",
    "liveness",
    "loudness",
    "speechiness",
    "valence",
    "tempo",
    "key",
    "mode",
    "time_signature",
]


spotify_audio_features_fields_with_0_to_1_range = [
    "acousticness",
    "danceability",
    "energy",
    "instrumentalness",
    "liveness",
    "speechiness",
    "valence",
]


def ensure_client(client=None) -> Spotify:
    if client is None:
        return get_spotify_client()
    if callable(client):
        client_factory = client
        client = client_factory()
    return client


# Note here TrackId
TrackRef = str  # can be an id, a url, a uri, a href...
TrackId = str  # really, TrackId is a string with a specific format, but don't know how to specify that type
TrackKey = Union[TrackRef, int, slice, Iterable[TrackRef]]
TrackMetadata = Dict[str, Any]


# TODO: Maybe use dol.KeyTemplate to implement casting (and other parsing and generation)?
import dol

TrackKeyKinds = Literal["uri", "id", "url", "href"]


track_ref_patterns = {
    "uri": r"^spotify:track:[\w]{22}$",
    "id": r"^[\w]{22}$",
    "url": r"^https://open.spotify.com/track/[\w]{22}$",
    "href": r"^https://api.spotify.com/v1/tracks/[\w]{22}$",
}


def cast_track_key(
    track_key: TrackRef,
    target_kind: TrackKeyKinds = "uri",
    *,
    src_kind: Optional[TrackKeyKinds] = None,
) -> TrackRef:
    """
    Convert a Spotify track key between different formats.

    Parameters:
        - track_key - the track key to convert
        - target_kind - the format to convert to (one of 'uri', 'id', 'url', 'href')
        - src_kind - the format of the input track key (optional)

    Returns:
        The track key in the target format.


    Examples:

    >>> cast_track_key("4iV5W9uYEdYUVa79Axb7Rh")
    'spotify:track:4iV5W9uYEdYUVa79Axb7Rh'
    >>> cast_track_key("spotify:track:4iV5W9uYEdYUVa79Axb7Rh", target_kind="id")
    '4iV5W9uYEdYUVa79Axb7Rh'
    >>> cast_track_key("4iV5W9uYEdYUVa79Axb7Rh", "url")
    'https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh'
    >>> cast_track_key('https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh', "href")
    'https://api.spotify.com/v1/tracks/4iV5W9uYEdYUVa79Axb7Rh'
    >>> cast_track_key("4iV5W9uYEdYUVa79Axb7Rh", "uri")
    'spotify:track:4iV5W9uYEdYUVa79Axb7Rh'

    """
    # Define possible patterns to detect the kind

    # Detect src_kind if not provided
    if src_kind is None:
        for kind, pattern in track_ref_patterns.items():
            if re.match(pattern, track_key):
                src_kind = kind
                break
        else:
            raise ValueError(
                f"Could not detect source kind for: {track_key=}"
                "Please specify a valid `src_kind`."
            )

    # Extract ID from the source format
    if src_kind == "uri":
        track_id = track_key.split(":")[-1]
    elif src_kind == "url" or src_kind == "href":
        track_id = track_key.split("/")[-1]
    elif src_kind == "id":
        track_id = track_key
    else:
        raise ValueError(f"Unsupported source kind: {src_kind}")

    # Convert to the target format
    if target_kind == "uri":
        return f"spotify:track:{track_id}"
    elif target_kind == "id":
        return track_id
    elif target_kind == "url":
        return f"https://open.spotify.com/track/{track_id}"
    elif target_kind == "href":
        return f"https://api.spotify.com/v1/tracks/{track_id}"
    else:
        raise ValueError(f"Unsupported target kind: {target_kind}")


ensure_track_id = partial(cast_track_key, target_kind="id")


# TODO: Make this complete
# TODO: Use dol.KeyTemplate to redo cast_track_key and the general playlist cast function
def ensure_playlist_id(playlist_spec: str) -> str:
    """
    Ensure that a playlist ID is in the correct format.

    Parameters:
        - playlist_id - the playlist ID to check

    Returns:
        The playlist ID in the correct format.

    Examples:

    >>> ensure_playlist_id("37i9dQZF1DXcBWIGoYBM5M")
    '37i9dQZF1DXcBWIGoYBM5M'
    >>> ensure_playlist_id("spotify:playlist:37i9dQZF1DXcBWIGoYBM5M")
    '37i9dQZF1DXcBWIGoYBM5M'
    >>> ensure_playlist_id("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
    '37i9dQZF1DXcBWIGoYBM5M'
    >>> ensure_playlist_id("https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M")
    '37i9dQZF1DXcBWIGoYBM5M'
    """
    if playlist_spec.startswith("spotify:playlist:"):
        return playlist_spec.split(":")[-1]
    elif playlist_spec.startswith("https://"):
        return playlist_spec.split("/")[-1].split("?")[0]
    else:
        return (
            playlist_spec  # just cross your fingers and hope it's a valid playlist ID
        )


front_columns_for_track_metas = (
    "name",
    "artists_names" "duration_ms",
    "popularity",
    "explicit",
    "album_name",
    "album_release_date",
    "album_release_year",
    "added_at_date",
    "url",
    "artist_list",
    "first_artist",
    "first_letter",
    "id",
)

back_columns_for_track_metas = (
    "type",
    "episode",
    "track",
    "album",
    "disc_number",
    "track_number",
    "artists",
    "preview_url",
    "uri",
    "href",
    "available_markets",
    "external_ids",
    "external_urls",
)


def move_columns_to_front(
    df: pd.DataFrame, columns: list[str], *, allow_excess=True
) -> pd.DataFrame:
    """
    Returns a copy of df with given columns in the front, in the order given.

    Parameters:
        - df - the DataFrame to modify
        - columns - the columns to move to the front
        - allow_excess - whether to allow columns not in the DataFrame (optional)

    Returns:
        The modified DataFrame.
    """
    if not allow_excess:
        assert set(columns) <= set(df.columns), "Columns not in DataFrame"
    columns = [col for col in columns if col in df.columns]
    return df[columns + [col for col in df.columns if col not in columns]]


def move_columns_to_back(
    df: pd.DataFrame, columns: list[str], *, allow_excess=True
) -> pd.DataFrame:
    """
    Returns a copy of df with given columns in the back, in the order given.

    Parameters:
        - df - the DataFrame to modify
        - columns - the columns to move to the back
        - allow_excess - whether to allow columns not in the DataFrame (optional)

    Returns:
        The modified DataFrame.
    """
    if not allow_excess:
        assert set(columns) <= set(df.columns), "Columns not in DataFrame"
    columns = [col for col in columns if col in df.columns]
    return df[[col for col in df.columns if col not in columns] + columns]
