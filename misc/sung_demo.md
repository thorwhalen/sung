```python

```

# Demo: Using the sung.base Module to Search Tracks and Create a Playlist

In this example, we’ll:
* Search for tracks using Tracks.search with a limit of 7.
* Display the search results in a pandas DataFrame.
* Select three tracks from the search results.
* Create a playlist called "my_test_playlist" with the selected tracks.
* Get the URL of the newly created playlist.
* Instantiate a Playlist object using a URL.
* Delete a playlist


Import the necessary classes from the sung.base module


```python
from sung.base import Tracks, Playlist
```

Search for tracks with the query 'Imagine', limiting the results to 7
This will return a Tracks object containing the search results


```python
tracks = Tracks.search(query='Love', limit=7)
```

Display the search results in a pandas DataFrame
The dataframe method converts the track metadata into a DataFrame for easy viewing


```python
df = tracks.dataframe()
print("Search Results:")
df.set_index('id') #[['id', 'name', 'artists', 'album']]
```

    Search Results:





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>album</th>
      <th>artists</th>
      <th>available_markets</th>
      <th>disc_number</th>
      <th>duration_ms</th>
      <th>explicit</th>
      <th>external_ids</th>
      <th>external_urls</th>
      <th>href</th>
      <th>is_local</th>
      <th>name</th>
      <th>popularity</th>
      <th>preview_url</th>
      <th>track_number</th>
      <th>type</th>
      <th>uri</th>
    </tr>
    <tr>
      <th>id</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>6FjErEvVbuC32xi4QJUXM0</th>
      <td>{'album_type': 'album', 'artists': [{'external...</td>
      <td>[{'external_urls': {'spotify': 'https://open.s...</td>
      <td>[AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, C...</td>
      <td>1</td>
      <td>187200</td>
      <td>False</td>
      <td>{'isrc': 'GBAYE6600300'}</td>
      <td>{'spotify': 'https://open.spotify.com/track/6F...</td>
      <td>https://api.spotify.com/v1/tracks/6FjErEvVbuC3...</td>
      <td>False</td>
      <td>Love for Sale</td>
      <td>23</td>
      <td>https://p.scdn.co/mp3-preview/d354e8a785bef3e4...</td>
      <td>13</td>
      <td>track</td>
      <td>spotify:track:6FjErEvVbuC32xi4QJUXM0</td>
    </tr>
    <tr>
      <th>1vrd6UOGamcKNGnSHJQlSt</th>
      <td>{'album_type': 'album', 'artists': [{'external...</td>
      <td>[{'external_urls': {'spotify': 'https://open.s...</td>
      <td>[CA, US]</td>
      <td>1</td>
      <td>235266</td>
      <td>False</td>
      <td>{'isrc': 'USCJY0803275'}</td>
      <td>{'spotify': 'https://open.spotify.com/track/1v...</td>
      <td>https://api.spotify.com/v1/tracks/1vrd6UOGamcK...</td>
      <td>False</td>
      <td>Love Story</td>
      <td>62</td>
      <td>None</td>
      <td>3</td>
      <td>track</td>
      <td>spotify:track:1vrd6UOGamcKNGnSHJQlSt</td>
    </tr>
    <tr>
      <th>3CeCwYWvdfXbZLXFhBrbnf</th>
      <td>{'album_type': 'single', 'artists': [{'externa...</td>
      <td>[{'external_urls': {'spotify': 'https://open.s...</td>
      <td>[AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, C...</td>
      <td>1</td>
      <td>235766</td>
      <td>False</td>
      <td>{'isrc': 'USUG12100342'}</td>
      <td>{'spotify': 'https://open.spotify.com/track/3C...</td>
      <td>https://api.spotify.com/v1/tracks/3CeCwYWvdfXb...</td>
      <td>False</td>
      <td>Love Story (Taylor’s Version)</td>
      <td>76</td>
      <td>None</td>
      <td>1</td>
      <td>track</td>
      <td>spotify:track:3CeCwYWvdfXbZLXFhBrbnf</td>
    </tr>
    <tr>
      <th>1dGr1c8CrMLDpV6mPbImSI</th>
      <td>{'album_type': 'album', 'artists': [{'external...</td>
      <td>[{'external_urls': {'spotify': 'https://open.s...</td>
      <td>[AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, C...</td>
      <td>1</td>
      <td>221306</td>
      <td>False</td>
      <td>{'isrc': 'USUG11901473'}</td>
      <td>{'spotify': 'https://open.spotify.com/track/1d...</td>
      <td>https://api.spotify.com/v1/tracks/1dGr1c8CrMLD...</td>
      <td>False</td>
      <td>Lover</td>
      <td>84</td>
      <td>None</td>
      <td>3</td>
      <td>track</td>
      <td>spotify:track:1dGr1c8CrMLDpV6mPbImSI</td>
    </tr>
    <tr>
      <th>0mbS3VwRbO6HVBMPXnzOGA</th>
      <td>{'album_type': 'album', 'artists': [{'external...</td>
      <td>[{'external_urls': {'spotify': 'https://open.s...</td>
      <td>[AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, C...</td>
      <td>1</td>
      <td>182000</td>
      <td>False</td>
      <td>{'isrc': 'GBAKW6701004'}</td>
      <td>{'spotify': 'https://open.spotify.com/track/0m...</td>
      <td>https://api.spotify.com/v1/tracks/0mbS3VwRbO6H...</td>
      <td>False</td>
      <td>To Love Somebody</td>
      <td>67</td>
      <td>None</td>
      <td>10</td>
      <td>track</td>
      <td>spotify:track:0mbS3VwRbO6HVBMPXnzOGA</td>
    </tr>
    <tr>
      <th>6dBUzqjtbnIa1TwYbyw5CM</th>
      <td>{'album_type': 'album', 'artists': [{'external...</td>
      <td>[{'external_urls': {'spotify': 'https://open.s...</td>
      <td>[AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, C...</td>
      <td>1</td>
      <td>213920</td>
      <td>False</td>
      <td>{'isrc': 'USHM21438143'}</td>
      <td>{'spotify': 'https://open.spotify.com/track/6d...</td>
      <td>https://api.spotify.com/v1/tracks/6dBUzqjtbnIa...</td>
      <td>False</td>
      <td>Lovers Rock</td>
      <td>85</td>
      <td>https://p.scdn.co/mp3-preview/922a42db5aa8f8d3...</td>
      <td>9</td>
      <td>track</td>
      <td>spotify:track:6dBUzqjtbnIa1TwYbyw5CM</td>
    </tr>
    <tr>
      <th>7hR22TOX3RorxJPcsz5Wbo</th>
      <td>{'album_type': 'single', 'artists': [{'externa...</td>
      <td>[{'external_urls': {'spotify': 'https://open.s...</td>
      <td>[AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, C...</td>
      <td>1</td>
      <td>204828</td>
      <td>False</td>
      <td>{'isrc': 'USUG12406387'}</td>
      <td>{'spotify': 'https://open.spotify.com/track/7h...</td>
      <td>https://api.spotify.com/v1/tracks/7hR22TOX3Ror...</td>
      <td>False</td>
      <td>Love Somebody</td>
      <td>86</td>
      <td>None</td>
      <td>1</td>
      <td>track</td>
      <td>spotify:track:7hR22TOX3RorxJPcsz5Wbo</td>
    </tr>
  </tbody>
</table>
</div>



Select three tracks from the search results
Here, we select the first three track IDs from the search results


```python
selected_track_ids = tracks.track_ids[:3]
print("\nSelected Track IDs:")
print(selected_track_ids)
```

    
    Selected Track IDs:
    ['6FjErEvVbuC32xi4QJUXM0', '1vrd6UOGamcKNGnSHJQlSt', '3CeCwYWvdfXbZLXFhBrbnf']


Create a new playlist named 'my_test_playlist' with the selected tracks
The create_from_track_list class method creates a new playlist with the given tracks


```python
playlist = Playlist.create_from_track_list(
    track_list=selected_track_ids,
    playlist_name='my_test_playlist'
)
print(f"\nPlaylist '{playlist.playlist_id}' created successfully.")

```

    
    Playlist '7BZcFvIWUnVzvZ5wpVt9cD' created successfully.


Get the playlist URL of the newly created playlist (go check it out!)


```python
playlist.playlist_url
```




    'https://open.spotify.com/playlist/7BZcFvIWUnVzvZ5wpVt9cD'



Instantiate a Playlist object using a URL.
This allows you to interact with the playlist, such as accessing its tracks


```python
playlist_obj = Playlist(playlist.playlist_url)
print("\nPlaylist Tracks:")
playlist_tracks_df = playlist_obj.dataframe()
playlist_tracks_df[['id', 'name', 'artists', 'album']]
```

    
    Playlist Tracks:





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>name</th>
      <th>artists</th>
      <th>album</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>6FjErEvVbuC32xi4QJUXM0</td>
      <td>Love for Sale</td>
      <td>[{'external_urls': {'spotify': 'https://open.s...</td>
      <td>{'available_markets': ['AR', 'AU', 'AT', 'BE',...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1vrd6UOGamcKNGnSHJQlSt</td>
      <td>Love Story</td>
      <td>[{'external_urls': {'spotify': 'https://open.s...</td>
      <td>{'available_markets': ['CA', 'US'], 'type': 'a...</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3CeCwYWvdfXbZLXFhBrbnf</td>
      <td>Love Story (Taylor’s Version)</td>
      <td>[{'external_urls': {'spotify': 'https://open.s...</td>
      <td>{'available_markets': ['AR', 'AU', 'AT', 'BE',...</td>
    </tr>
  </tbody>
</table>
</div>




```python
playlist_tracks_df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>preview_url</th>
      <th>available_markets</th>
      <th>explicit</th>
      <th>type</th>
      <th>episode</th>
      <th>track</th>
      <th>album</th>
      <th>artists</th>
      <th>disc_number</th>
      <th>track_number</th>
      <th>duration_ms</th>
      <th>external_ids</th>
      <th>external_urls</th>
      <th>href</th>
      <th>id</th>
      <th>name</th>
      <th>popularity</th>
      <th>uri</th>
      <th>is_local</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>https://p.scdn.co/mp3-preview/d354e8a785bef3e4...</td>
      <td>[AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, C...</td>
      <td>False</td>
      <td>track</td>
      <td>False</td>
      <td>True</td>
      <td>{'available_markets': ['AR', 'AU', 'AT', 'BE',...</td>
      <td>[{'external_urls': {'spotify': 'https://open.s...</td>
      <td>1</td>
      <td>13</td>
      <td>187200</td>
      <td>{'isrc': 'GBAYE6600300'}</td>
      <td>{'spotify': 'https://open.spotify.com/track/6F...</td>
      <td>https://api.spotify.com/v1/tracks/6FjErEvVbuC3...</td>
      <td>6FjErEvVbuC32xi4QJUXM0</td>
      <td>Love for Sale</td>
      <td>23</td>
      <td>spotify:track:6FjErEvVbuC32xi4QJUXM0</td>
      <td>False</td>
    </tr>
    <tr>
      <th>1</th>
      <td>https://p.scdn.co/mp3-preview/7bc39c6033766fc8...</td>
      <td>[CA, US]</td>
      <td>False</td>
      <td>track</td>
      <td>False</td>
      <td>True</td>
      <td>{'available_markets': ['CA', 'US'], 'type': 'a...</td>
      <td>[{'external_urls': {'spotify': 'https://open.s...</td>
      <td>1</td>
      <td>3</td>
      <td>235266</td>
      <td>{'isrc': 'USCJY0803275'}</td>
      <td>{'spotify': 'https://open.spotify.com/track/1v...</td>
      <td>https://api.spotify.com/v1/tracks/1vrd6UOGamcK...</td>
      <td>1vrd6UOGamcKNGnSHJQlSt</td>
      <td>Love Story</td>
      <td>62</td>
      <td>spotify:track:1vrd6UOGamcKNGnSHJQlSt</td>
      <td>False</td>
    </tr>
    <tr>
      <th>2</th>
      <td>https://p.scdn.co/mp3-preview/b2c1ed4794591a62...</td>
      <td>[AR, AU, AT, BE, BO, BR, BG, CA, CL, CO, CR, C...</td>
      <td>False</td>
      <td>track</td>
      <td>False</td>
      <td>True</td>
      <td>{'available_markets': ['AR', 'AU', 'AT', 'BE',...</td>
      <td>[{'external_urls': {'spotify': 'https://open.s...</td>
      <td>1</td>
      <td>1</td>
      <td>235766</td>
      <td>{'isrc': 'USUG12100342'}</td>
      <td>{'spotify': 'https://open.spotify.com/track/3C...</td>
      <td>https://api.spotify.com/v1/tracks/3CeCwYWvdfXb...</td>
      <td>3CeCwYWvdfXbZLXFhBrbnf</td>
      <td>Love Story (Taylor’s Version)</td>
      <td>76</td>
      <td>spotify:track:3CeCwYWvdfXbZLXFhBrbnf</td>
      <td>False</td>
    </tr>
  </tbody>
</table>
</div>



Delete a playlist

We purposely tried to make deleting a playlist not as easy as the other actions. 
So we didn't attach a delete method to the playlist instance, but put this in a 
separate function you have to import. 
Also, we made that function verbose, and asking for confirmation by default. 
(But there's arguments to control that, so you can use `functools.partial` to 
make your own cowboy (not speaking and not asking for permission) version).


```python
from sung import delete_playlist

delete_playlist(playlist.playlist_id)
```

    Playlist 7BZcFvIWUnVzvZ5wpVt9cD has been deleted (unfollowed).



```python

```


```python

```


```python

```


```python

```


```python

```
