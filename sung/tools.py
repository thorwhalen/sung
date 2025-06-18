"""Tools using sung"""

import pandas as pd
from collections import defaultdict, Counter
from functools import cached_property, partial
from typing import Optional

from sung.base import PlaylistReader, extra_track_metadata_extractions
from sung.util import (
    move_columns_to_front,
    front_columns_for_track_metas,
    extractor,
    ensure_playlist_id,
    get_spotify_client,
    SpotifyFeaturesT,
    spotify_features_field_names,
    spotify_features_fields,
    convert_date,
)
from dol import wrap_kvs


# --------------------------------------------------------------------------------------
# Prepared data accessors

# Code to access thorwhalen/sung_content data with ease

DFLT_GITHUB_BRANCH = "main"
DFLT_REPO_STUB = f"thorwhalen/sung_content"


# Note: hubcap has tools for url manipulation, but it's overkill for this simple case
def raw_github_url(
    path=None,
    *,
    repo_stub=DFLT_REPO_STUB,
    branch=None,
    url_prefix="https://raw.githubusercontent.com",
):
    """
    Return the raw github url for a given path in a given repo and branch.

    By default, the repo_stub is 'thorwhalen/sung_content' and the branch is 'main'.

    >>> raw_github_url('parquet/greatest_500_songs.parquet')
    'https://raw.githubusercontent.com/thorwhalen/sung_content/main/parquet/greatest_500_songs.parquet'

    If the path is not given, return a partial function that takes the path as argument.
    That is, will make a "path to url" function for a given repo and branch.

    >>> get_url = raw_github_url(repo_stub='thorwhalen/content', branch='master')
    >>> get_url('tables/csv/named_urls.csv')
    'https://raw.githubusercontent.com/thorwhalen/content/master/tables/csv/named_urls.csv'

    """
    if path is None:
        return partial(raw_github_url, repo_stub=repo_stub, branch=branch)

    if branch is None:
        if len(repo_stub.split("/")) == 3:
            branch = repo_stub.split("/")[2]
        else:
            branch = DFLT_GITHUB_BRANCH

    return f"{url_prefix}/{repo_stub}/{branch}/{path}"


def get_content_bytes(
    key, max_age=None, *, cache_locally=False, content_url=raw_github_url
):
    """Get bytes of content from `thorwhalen/content`, automatically caching locally.

    ```
    # add max_age=1e-6 if you want to update the data with the remote data
    b = get_content_bytes('tables/csv/projects.csv', max_age=None)
    ```
    """
    url = content_url(key)

    if cache_locally:
        from graze import graze
        import os

        if isinstance(cache_locally, str):
            rootdir = cache_locally
            assert os.path.isdir(
                rootdir
            ), f"cache_locally: {rootdir} is not a directory"
            return graze(url, rootdir, max_age=max_age)
        return graze(url, max_age=max_age)
    else:
        import requests

        return requests.get(url).content


def get_github_table(
    key,
    max_age=None,
    *,
    content_url=raw_github_url,
    get_content_bytes=get_content_bytes,
    **extra_decoder_kwargs,
):
    from tabled import get_table

    bytes_ = get_content_bytes(key, max_age=max_age, content_url=content_url)
    ext = key.split(".")[-1] if "." in key else None
    return get_table(bytes_, ext=ext, **extra_decoder_kwargs)


# --------------------------------------------------------------------------------------
# Track Analysis

_standard = {
    "name": "name",
    "duration_ms": "duration_ms",
    "popularity": "popularity",
    "explicit": "explicit",
}
standard_meta_data_extractions = dict(**_standard, **extra_track_metadata_extractions)
standard_extraction = extractor(standard_meta_data_extractions)


class TracksAnalysis:
    def __init__(self, playlist):
        if isinstance(playlist, pd.DataFrame):
            self.df = playlist
            self.playlist_id = None
            self.playlist_url = None
        else:
            if isinstance(playlist, PlaylistReader):
                self.playlist = playlist
                self.playlist_id = playlist.playlist_id
                self.playlist_url = playlist.playlist_url
            else:
                playlist_id = ensure_playlist_id(playlist)
                self.playlist_id = playlist_id
                self.playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
                self.playlist = wrap_kvs(
                    PlaylistReader(self.playlist_url),
                    value_decoder=standard_extraction,
                )
            # create the base dataframe
            self.df = self.playlist.data
            # and manipulate it
            self._process_dataframe()
            self._add_added_at_dates()
            self._reorder_and_sort_dataframe()

    def _process_dataframe(self):
        """Process the dataframe to extract and compute necessary columns."""

        df = self.df
        # df['first_artist'] = df['artists'].apply(lambda x: x[0]['name'] if x else None)
        # df['album_name'] = df['album'].apply(
        #     lambda x: x.get('name', None) if x else None
        # )
        # df['url'] = df['external_urls'].apply(
        #     lambda x: x.get('spotify', None) if x else None
        # )
        df["first_letter"] = df["name"].str[0].str.upper()
        # df['album_release_date'] = df['album'].apply(
        #     lambda x: x.get('release_date', None) if x else None
        # )
        # df['album_release_date'] = df['album_release_date'].apply(convert_date)
        # df['album_release_year'] = df['album_release_date'].str[:4].astype(int)
        self.df = df

    def _add_added_at_dates(self):
        """Add the 'added_at' date for each track in the playlist."""
        sp = get_spotify_client(ensure_scope="playlist-read-private")
        playlist_tracks = []
        offset = 0
        limit = 100
        while True:
            response = sp.playlist_tracks(self.playlist_id, offset=offset, limit=limit)
            playlist_tracks.extend(response["items"])
            if len(response["items"]) < limit:
                break
            offset += limit

        added_at_data = [
            {"added_at_datetime": item["added_at"], "id": item["track"]["id"]}
            for item in playlist_tracks
        ]
        added_at_df = pd.DataFrame(added_at_data)
        added_at_df["added_at_date"] = added_at_df["added_at_datetime"].str[:10]

        # Merge with the main dataframe
        self.df = pd.merge(
            self.df, added_at_df, left_index=True, right_index=True, how="left"
        )
        self.df["id"] = self.df.index.values

    def _reorder_and_sort_dataframe(self):
        """Reorder columns and sort the dataframe by 'added_at_date'."""
        self.df = move_columns_to_front(self.df, front_columns_for_track_metas)
        self.df = self.df.sort_values("added_at_date", ascending=False)

    @cached_property
    def names(self):
        """List of all track names."""
        return self.df["name"]

    @cached_property
    def number_of_songs(self):
        """Total number of songs in the playlist."""
        return len(self.names)

    @cached_property
    def unique_names(self):
        """Set of unique track names."""
        return set(self.names)

    @cached_property
    def number_of_unique_names(self):
        """Number of unique track names."""
        return len(self.unique_names)

    @cached_property
    def name_counts(self):
        """Counter of track names."""
        return Counter(self.names)

    @cached_property
    def duplicates(self):
        """Dictionary of duplicate track names and their counts."""
        return {name: count for name, count in self.name_counts.items() if count > 1}

    def print_duplicates(self):
        """Print duplicate track names and their counts."""
        duplicates_series = pd.Series(self.duplicates, name="count")
        print("\n### Duplicates")
        print(duplicates_series.to_markdown())

    def most_popular_songs(self, n=20):
        """Return the top 'n' most popular songs."""
        df = self.df
        top_n = df.sort_values("popularity", ascending=False).head(n)
        return top_n[["name", "first_artist", "popularity"]]

    def print_most_popular_songs(self, n=20):
        """Print the top 'n' most popular songs."""
        top_n = self.most_popular_songs(n)
        print(top_n.to_markdown(index=False))

    @cached_property
    def artist_counts(self):
        """Series of artist counts."""
        return self.df["first_artist"].value_counts()

    def print_top_artists(self, n=25):
        """Print the top 'n' artists by song count."""
        print(self.artist_counts.head(n).to_markdown())

    @cached_property
    def songs_by_release_year(self):
        """Dataframe grouping songs by their release year."""
        df = self.df.copy()
        df["name_and_artist"] = df["name"] + " -- " + df["first_artist"]
        grouped = (
            df.groupby("album_release_year")["name_and_artist"]
            .apply(list)
            .reset_index()
        )
        grouped["number_of_songs"] = grouped["name_and_artist"].apply(len)
        grouped = grouped.sort_values("album_release_year").set_index(
            "album_release_year"
        )
        return grouped

    def plot_songs_per_year(self):
        """Plot the number of songs per release year."""
        from oplot import dict_bar_plot  # pip install oplot  # noqa

        grouped = self.songs_by_release_year
        song_counts = grouped["number_of_songs"].to_dict()
        annotations = {
            year: names[0]
            for year, names in grouped["name_and_artist"].to_dict().items()
        }
        dict_bar_plot(
            song_counts,
            annotations=annotations,
            annotations_cutoff_length=20,
            title="Number of Songs per Year",
        )

    @cached_property
    def dates(self):
        """Dataframe containing 'album_release_date' and 'added_at_date'."""
        df = self.df.copy()
        df = df[
            [
                "album_release_date",
                "added_at_date",
                "name",
                "first_artist",
                "album_release_year",
            ]
        ]
        df["name_and_artist"] = df["name"] + " -- " + df["first_artist"]
        df["album_release_date"] = pd.to_datetime(df["album_release_date"])
        df["added_at_date"] = pd.to_datetime(df["added_at_date"])
        return df

    @cached_property
    def tracks_grouped_by_year(self):
        g = self.dates.groupby("album_release_year")["name_and_artist"].apply(list)
        g = g.reset_index()
        # grouped['name_and_artist'] = grouped['name_and_artist'].apply(lambda x: "\n".join(x))
        g["number_of_songs"] = g["name_and_artist"].apply(len)
        g = g.sort_values("album_release_year").set_index("album_release_year")
        return g

    def plot_added_vs_release_dates(self):
        """Plot 'added_at_date' versus 'album_release_date'."""
        import seaborn as sns  # pip install seaborn  # noqa

        dates = self.dates
        sns.set_theme(style="whitegrid")
        sns.scatterplot(data=dates, x="added_at_date", y="album_release_date", s=100)

    def plot_added_vs_release_kde(self):
        """Plot a KDE of 'added_at_date' versus 'album_release_date'."""
        import seaborn as sns  # pip install seaborn  # noqa

        dates = self.dates
        sns.kdeplot(
            data=dates,
            x="added_at_date",
            y="album_release_date",
            cmap="viridis",
            fill=True,
            bw_adjust=0.7,
        )

    def plot_added_vs_release_kde_boundary(self):
        """Plot a KDE with a boundary condition where 'album_release_date' <= 'added_at_date'."""
        from oplot import kdeplot_w_boundary_condition  # pip install oplot  # noqa

        dates = self.dates
        kdeplot_w_boundary_condition(
            data=dates,
            x="added_at_date",
            y="album_release_date",
            cmap="viridis",
            fill=True,
            bw_adjust=0.7,
            boundary_condition=lambda x, y: y <= x,
        )

    @cached_property
    def first_letter_counts(self):
        """Dictionary of counts of track names by their first letter."""
        names = self.names
        name_groups = defaultdict(list)
        for name in names:
            name_groups[name[0].lower()].append(name)
        letter_counts = {letter: len(names) for letter, names in name_groups.items()}
        return letter_counts

    def plot_first_letter_distribution(self, sort_by="lexicographical"):
        """Plot the distribution of first letters in track names."""
        from oplot import dict_bar_plot  # pip install oplot  # noqa

        letter_counts = self.first_letter_counts
        if sort_by == "lexicographical":
            sorted_counts = dict(sorted(letter_counts.items(), key=lambda x: x[0]))
            title = "First Letter Distribution (Lexicographical Order)"
        elif sort_by == "count":
            sorted_counts = dict(
                sorted(letter_counts.items(), key=lambda x: x[1], reverse=True)
            )
            title = "First Letter Distribution (Sorted by Count)"
        else:
            sorted_counts = letter_counts
            title = "First Letter Distribution"

        dict_bar_plot(sorted_counts, title=title)

    def get_top_names_by_letter(self, n=20):
        """Get up to 'n' top tracks for each starting letter, sorted by popularity."""
        name_groups = defaultdict(list)
        for name in self.names:
            name_groups[name[0].lower()].append(name)

        top_names = {}
        for letter, names in name_groups.items():
            if names:
                top_tracks = self.df[self.df["name"].isin(names)].nlargest(
                    n, "popularity"
                )
                top_names[letter] = top_tracks["name"].tolist()
        return top_names

    def print_top_names_by_letter(self, n=20):
        """Print up to 'n' top tracks for each starting letter."""
        top_names = self.get_top_names_by_letter(n)
        for letter, names in top_names.items():
            print(f"{letter.upper()} ({len(names)} tracks):")
            for name in names:
                popularity = self.df[self.df["name"] == name]["popularity"].values[0]
                print(f"  - ({popularity}) {name}")

    def plot_features_histogram(
        self,
        feature: SpotifyFeaturesT = "popularity",
        bins=20,
        xlim=None,
        ylim=None,
    ):
        """Plot the histogram of a given audio feature."""
        import seaborn as sns
        from matplotlib import pyplot as plt

        sns.histplot(self.playlist.numerical_features_df[feature], bins=bins)
        plt.xlabel(feature)
        plt.ylabel("Count")

        if xlim is not None:
            plt.xlim(*xlim)
        if ylim is not None:
            plt.ylim(*ylim)

    def plot_features_scatter(
        self,
        x: SpotifyFeaturesT = "danceability",
        y: SpotifyFeaturesT = "energy",
        hue: SpotifyFeaturesT = "loudness",
        size: SpotifyFeaturesT = "popularity",
        *,
        xlim=None,
        ylim=None,
        annotation_field: Optional[SpotifyFeaturesT] = None,
        **scatterplot_kwargs,
    ):
        """Return the audio features dataframe."""
        import seaborn as sns
        from matplotlib import pyplot as plt

        df = pd.merge(
            self.playlist.data,
            self.playlist.audio_features_df,
            left_index=True,
            right_index=True,
        )
        # scatter plot with danceability and energy, colored by popularity, with size as loudness
        sns.scatterplot(data=df, x=x, y=y, hue=hue, size=size, **scatterplot_kwargs)

        # Move the legend outside the plot
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

        from sung.util import spotify_audio_features_fields_with_0_to_1_range

        # if x and/or y are in the 0 to 1 range, set the x and y limits to 0 and 1
        if xlim is None:
            if x in spotify_audio_features_fields_with_0_to_1_range:
                xlim = (0, 1)
        if ylim is None:
            if y in spotify_audio_features_fields_with_0_to_1_range:
                ylim = (0, 1)

        if xlim is not None:
            plt.xlim(*xlim)
        if ylim is not None:
            plt.ylim(*ylim)

        if annotation_field:
            for i, row in df.iterrows():
                plt.text(row[x], row[y], row[annotation_field])

    def plot_dataframe_distributions(self, *, n_columns=4, kde=False, bins=30):
        """
        Plots the distributions of all columns in the given DataFrame as histograms.

        Parameters:
            df (pd.DataFrame): The DataFrame whose columns' distributions are to be plotted.
            n_columns (int): Number of columns in the grid layout for the plots (default is 4).

        Returns:
            plt.Figure: The matplotlib figure containing the histograms.
        """
        from matplotlib import pyplot as plt
        import seaborn as sns

        df = self.playlist.numerical_features_df

        # Number of columns in the DataFrame
        n_cols = len(df.columns)

        # Number of rows needed for the given number of columns
        n_rows = (n_cols + n_columns - 1) // n_columns

        # Create the figure and axes
        fig, axes = plt.subplots(n_rows, n_columns, figsize=(5 * n_columns, 4 * n_rows))
        axes = axes.flatten()  # Flatten axes to iterate easily

        # Plot histograms for each column
        for i, column in enumerate(df.columns):
            sns.histplot(df[column].dropna(), kde=kde, ax=axes[i], bins=bins)
            axes[i].set_title(column)
            axes[i].set_xlabel("Value")
            axes[i].set_ylabel("Frequency")

        # Hide unused axes if any
        for i in range(n_cols, len(axes)):
            axes[i].set_visible(False)

        plt.tight_layout()

    def plot_features_pairs(
        self,
        features=spotify_features_field_names,
    ):
        """Return the audio features pairplot."""
        import seaborn as sns

        sns.pairplot(self.playlist.numerical_features_df[list(features)])
