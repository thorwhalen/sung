# Analyze a playlist


```python
from sung import TracksAnalysis, ensure_playlist_id

```

## Initialize the Class with a Playlist ID


```python
# Let's analyze my daughter's playlist...

playlist = "https://open.spotify.com/playlist/4nEeS47ineUShHK2iAVeO0?si=be16c62b664f43f3"

ta = TracksAnalysis(playlist)
```

Note that, alternatively, if you already have a dataframe, you can just give `TracksAnalysis` that.
Note that it must have been prepared by `TracksAnalysis`, or at least satisfy the dataframe conditions on the columns. 


```python
# import pandas as pd
# df = pd.read_excel("~/Dropbox/_odata/ai_contexts/misc/music/encore_playlist.xlsx")
# ta = TracksAnalysis(df)
```

## Access the Processed Dataframe


```python
ta.df.head()

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
      <th>name</th>
      <th>first_artist</th>
      <th>duration_ms</th>
      <th>popularity</th>
      <th>explicit</th>
      <th>album_release_date</th>
      <th>album_release_year</th>
      <th>added_at_date</th>
      <th>url</th>
      <th>first_letter</th>
      <th>...</th>
      <th>artists</th>
      <th>disc_number</th>
      <th>track_number</th>
      <th>external_ids</th>
      <th>external_urls</th>
      <th>href</th>
      <th>uri</th>
      <th>is_local</th>
      <th>added_at_datetime</th>
      <th>id_y</th>
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
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>62HY7V5hRKtfIZ7uCYqYqu</th>
      <td>The Imperial March (Darth Vader's Theme)</td>
      <td>John Williams</td>
      <td>182973</td>
      <td>0</td>
      <td>False</td>
      <td>1997-01-01</td>
      <td>1997</td>
      <td>NaN</td>
      <td>https://open.spotify.com/track/62HY7V5hRKtfIZ7...</td>
      <td>T</td>
      <td>...</td>
      <td>[{'external_urls': {'spotify': 'https://open.s...</td>
      <td>2</td>
      <td>1</td>
      <td>{'isrc': 'USSM10411815'}</td>
      <td>{'spotify': 'https://open.spotify.com/track/62...</td>
      <td>https://api.spotify.com/v1/tracks/62HY7V5hRKtf...</td>
      <td>spotify:track:62HY7V5hRKtfIZ7uCYqYqu</td>
      <td>False</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>0mVL6TMwrRqFsLRgoKoAfS</th>
      <td>Wimoweh (Mbube)</td>
      <td>Yma Sumac</td>
      <td>158440</td>
      <td>0</td>
      <td>False</td>
      <td>2015-01-28</td>
      <td>2015</td>
      <td>NaN</td>
      <td>https://open.spotify.com/track/0mVL6TMwrRqFsLR...</td>
      <td>W</td>
      <td>...</td>
      <td>[{'external_urls': {'spotify': 'https://open.s...</td>
      <td>1</td>
      <td>4</td>
      <td>{'isrc': 'FR0W61497652'}</td>
      <td>{'spotify': 'https://open.spotify.com/track/0m...</td>
      <td>https://api.spotify.com/v1/tracks/0mVL6TMwrRqF...</td>
      <td>spotify:track:0mVL6TMwrRqFsLRgoKoAfS</td>
      <td>False</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3N7aUWtL9EvKrBtmSCxuYW</th>
      <td>Mah Na Mah Na</td>
      <td>Mahna Mahna and The Two Snowths</td>
      <td>125906</td>
      <td>10</td>
      <td>False</td>
      <td>2011-01-01</td>
      <td>2011</td>
      <td>NaN</td>
      <td>https://open.spotify.com/track/3N7aUWtL9EvKrBt...</td>
      <td>M</td>
      <td>...</td>
      <td>[{'external_urls': {'spotify': 'https://open.s...</td>
      <td>1</td>
      <td>30</td>
      <td>{'isrc': 'USWD11158969'}</td>
      <td>{'spotify': 'https://open.spotify.com/track/3N...</td>
      <td>https://api.spotify.com/v1/tracks/3N7aUWtL9EvK...</td>
      <td>spotify:track:3N7aUWtL9EvKrBtmSCxuYW</td>
      <td>False</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1XieuY2bxCfXNHwSDJQrPs</th>
      <td>My Baby Just Cares For Me</td>
      <td>Nina Simone</td>
      <td>215706</td>
      <td>36</td>
      <td>False</td>
      <td>2007-01-01</td>
      <td>2007</td>
      <td>NaN</td>
      <td>https://open.spotify.com/track/1XieuY2bxCfXNHw...</td>
      <td>M</td>
      <td>...</td>
      <td>[{'external_urls': {'spotify': 'https://open.s...</td>
      <td>1</td>
      <td>8</td>
      <td>{'isrc': 'USPR38700001'}</td>
      <td>{'spotify': 'https://open.spotify.com/track/1X...</td>
      <td>https://api.spotify.com/v1/tracks/1XieuY2bxCfX...</td>
      <td>spotify:track:1XieuY2bxCfXNHwSDJQrPs</td>
      <td>False</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>40Fr7DB1j6RB2DqygQI4LI</th>
      <td>Holocaust</td>
      <td>Ceza</td>
      <td>207746</td>
      <td>57</td>
      <td>False</td>
      <td>2004-07-01</td>
      <td>2004</td>
      <td>NaN</td>
      <td>https://open.spotify.com/track/40Fr7DB1j6RB2Dq...</td>
      <td>H</td>
      <td>...</td>
      <td>[{'external_urls': {'spotify': 'https://open.s...</td>
      <td>1</td>
      <td>3</td>
      <td>{'isrc': 'TR0640600079'}</td>
      <td>{'spotify': 'https://open.spotify.com/track/40...</td>
      <td>https://api.spotify.com/v1/tracks/40Fr7DB1j6RB...</td>
      <td>spotify:track:40Fr7DB1j6RB2DqygQI4LI</td>
      <td>False</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 29 columns</p>
</div>



## Audio Features Analysis


```python
ta.plot_features_histogram()
```


    
![png](https://raw.githubusercontent.com/thorwhalen/sung/main/misc/playlist_analysis_files/playlist_analysis_10_0.png)
    



```python
ta.plot_features_scatter()

```


    
![png](https://raw.githubusercontent.com/thorwhalen/sung/main/misc/playlist_analysis_files/playlist_analysis_11_0.png)
    


You can choose what fields to map to what plot features (x, y, size and hue). 

The names of the audio feature fields with their descriptions, are 


```python
from sung.util import spotify_features_fields

spotify_features_fields
```




    {'name': 'The name of the track.',
     'artist': 'The name of the primary artist associated with the track.',
     'album': 'The name of the album in which the track appears.',
     'release_date': 'The release date of the album or single. Format can vary (e.g., YYYY-MM-DD).',
     'duration_ms': "The track's duration in milliseconds.",
     'popularity': 'The popularity of the track, with values ranging from 0 to 100. Higher values indicate greater popularity.',
     'explicit': 'A boolean indicating whether the track contains explicit content.',
     'external_url': 'A dictionary of external URLs, including a link to the track on Spotify.',
     'preview_url': 'A URL to a 30-second preview of the track, if available.',
     'track_number': "The track's position within its album or single. The first track is 1.",
     'album_total_tracks': 'The total number of tracks in the album that contains this track.',
     'available_markets': 'A list of country codes where the track is available.',
     'album_images': 'A list of album cover art images in various sizes, with URLs to access them.',
     'acousticness': 'A confidence measure from 0.0 to 1.0 indicating the likelihood that the track is acoustic. Higher values denote a higher probability. Range: 0.0 to 1.0.',
     'danceability': 'Reflects how suitable a track is for dancing, based on tempo, rhythm stability, beat strength, and overall regularity. Higher values indicate greater danceability. Range: 0.0 to 1.0.',
     'energy': 'Measures the intensity and activity of a track. Energetic tracks feel fast, loud, and noisy. Higher values represent more energy. Range: 0.0 to 1.0.',
     'instrumentalness': 'Predicts whether a track contains no vocals. Higher values suggest a greater likelihood of the track being instrumental. Range: 0.0 to 1.0.',
     'liveness': 'Detects the presence of an audience in the recording. Higher values indicate a higher probability of the track being performed live. Range: 0.0 to 1.0.',
     'loudness': 'The overall loudness of a track in decibels (dB), averaged across the entire track. Useful for comparing the relative loudness of tracks. Typical range: -60 to 0 dB.',
     'speechiness': 'Measures the presence of spoken words in a track. Higher values indicate more speech-like content. Values above 0.66 suggest tracks made entirely of spoken words; values between 0.33 and 0.66 may contain both music and speech; values below 0.33 likely represent music and other non-speech-like tracks. Range: 0.0 to 1.0.',
     'valence': 'Describes the musical positiveness conveyed by a track. Higher values sound more positive (e.g., happy, cheerful), while lower values sound more negative (e.g., sad, angry). Range: 0.0 to 1.0.',
     'tempo': 'The estimated tempo of a track in beats per minute (BPM). Range: 0 to 250 BPM.',
     'key': 'The estimated overall key of the track, represented as an integer corresponding to standard Pitch Class notation (e.g., 0 = C, 1 = C♯/D♭, ..., 11 = B). If no key was detected, the value is -1. Range: -1 to 11.',
     'mode': 'Indicates the modality (major or minor) of a track. Major is represented by 1 and minor by 0. Range: 0 or 1.',
     'time_signature': 'An estimated overall time signature of a track, indicating how many beats are in each bar. Range: 3 to 7.'}




```python
ta.plot_features_scatter(x='valence', y='tempo', hue='key')
```


    
![png](https://raw.githubusercontent.com/thorwhalen/sung/main/misc/playlist_analysis_files/playlist_analysis_14_0.png)
    



```python

```


```python
ta.plot_dataframe_distributions()
```


    
![png](https://raw.githubusercontent.com/thorwhalen/sung/main/misc/playlist_analysis_files/playlist_analysis_16_0.png)
    



```python
ta.plot_features_pairs()
```




    <seaborn.axisgrid.PairGrid at 0x3291ac1f0>




    
![png](https://raw.githubusercontent.com/thorwhalen/sung/main/misc/playlist_analysis_files/playlist_analysis_17_1.png)
    



```python

```

## Metadata Analyses


```python
print(f"Number of songs: {ta.number_of_songs}")
print(f"Number of unique names: {ta.number_of_unique_names}")
```

    Number of songs: 182
    Number of unique names: 178


### Print Duplicates


```python
ta.print_duplicates()
```

    
    ### Duplicates
    |                              |   count |
    |:-----------------------------|--------:|
    | Houdini                      |       2 |
    | Anything You Can Do          |       2 |
    | Somebody That I Used to Know |       2 |
    | The Bare Necessities         |       2 |


### Print Most Popular Songs


```python
ta.print_most_popular_songs(n=20)
```

    | name                                            | first_artist      |   popularity |
    |:------------------------------------------------|:------------------|-------------:|
    | Espresso                                        | Sabrina Carpenter |           90 |
    | exes                                            | Tate McRae        |           83 |
    | Sweet Dreams (Are Made of This) - 2005 Remaster | Eurythmics        |           83 |
    | Zombie                                          | The Cranberries   |           82 |
    | Here Comes The Sun - Remastered 2009            | The Beatles       |           82 |
    | Before You Go                                   | Lewis Capaldi     |           81 |
    | bad guy                                         | Billie Eilish     |           81 |
    | ...Baby One More Time                           | Britney Spears    |           81 |
    | Tainted Love                                    | Soft Cell         |           79 |
    | Wrecking Ball                                   | Miley Cyrus       |           78 |
    | New Rules                                       | Dua Lipa          |           78 |
    | Rolling in the Deep                             | Adele             |           77 |
    | Kings & Queens                                  | Ava Max           |           77 |
    | Easy On Me                                      | Adele             |           77 |
    | Roar                                            | Katy Perry        |           77 |
    | bellyache                                       | Billie Eilish     |           76 |
    | Jolene                                          | Dolly Parton      |           75 |
    | Symphony (feat. Zara Larsson)                   | Clean Bandit      |           75 |
    | Nice For What                                   | Drake             |           74 |
    | bury a friend                                   | Billie Eilish     |           74 |


### Print Top Artists


```python
ta.print_top_artists(n=25)
```

    | first_artist       |   count |
    |:-------------------|--------:|
    | Dua Lipa           |       6 |
    | Eminem             |       5 |
    | Jacob Collier      |       4 |
    | Norris Nuts        |       4 |
    | The Beatles        |       4 |
    | Hugh Jackman       |       4 |
    | Music Together     |       3 |
    | Leonard Bernstein  |       3 |
    | Julie Andrews      |       3 |
    | Walk off the Earth |       3 |
    | John Williams      |       3 |
    | Billie Eilish      |       3 |
    | Anna Kendrick      |       3 |
    | Zac Efron          |       2 |
    | Clean Bandit       |       2 |
    | Adele              |       2 |
    | Shakira            |       2 |
    | Stromae            |       2 |
    | Michael Jackson    |       2 |
    | Lin-Manuel Miranda |       2 |
    | Caravan Palace     |       2 |
    | Queen              |       2 |
    | Ynairaly Simo      |       2 |
    | Édith Piaf         |       2 |
    | Dolly Parton       |       1 |


### Plot Number of Songs per Release Year


```python
ta.plot_songs_per_year()
```

    /Users/thorwhalen/.pyenv/versions/3.10.13/envs/p10/lib/python3.10/site-packages/IPython/core/pylabtools.py:170: UserWarning: Glyph 44053 (\N{HANGUL SYLLABLE GANG}) missing from font(s) DejaVu Sans.
      fig.canvas.print_figure(bytes_io, **kw)
    /Users/thorwhalen/.pyenv/versions/3.10.13/envs/p10/lib/python3.10/site-packages/IPython/core/pylabtools.py:170: UserWarning: Glyph 45224 (\N{HANGUL SYLLABLE NAM}) missing from font(s) DejaVu Sans.
      fig.canvas.print_figure(bytes_io, **kw)
    /Users/thorwhalen/.pyenv/versions/3.10.13/envs/p10/lib/python3.10/site-packages/IPython/core/pylabtools.py:170: UserWarning: Glyph 49828 (\N{HANGUL SYLLABLE SEU}) missing from font(s) DejaVu Sans.
      fig.canvas.print_figure(bytes_io, **kw)
    /Users/thorwhalen/.pyenv/versions/3.10.13/envs/p10/lib/python3.10/site-packages/IPython/core/pylabtools.py:170: UserWarning: Glyph 53440 (\N{HANGUL SYLLABLE TA}) missing from font(s) DejaVu Sans.
      fig.canvas.print_figure(bytes_io, **kw)
    /Users/thorwhalen/.pyenv/versions/3.10.13/envs/p10/lib/python3.10/site-packages/IPython/core/pylabtools.py:170: UserWarning: Glyph 51068 (\N{HANGUL SYLLABLE IL}) missing from font(s) DejaVu Sans.
      fig.canvas.print_figure(bytes_io, **kw)



    
![png](https://raw.githubusercontent.com/thorwhalen/sung/main/misc/playlist_analysis_files/playlist_analysis_28_1.png)
    


### Plot Added Date vs. Release Date


```python
ta.plot_added_vs_release_dates()
```


    
![png](https://raw.githubusercontent.com/thorwhalen/sung/main/misc/playlist_analysis_files/playlist_analysis_30_0.png)
    



```python
ta.plot_added_vs_release_kde()
```


    
![png](https://raw.githubusercontent.com/thorwhalen/sung/main/misc/playlist_analysis_files/playlist_analysis_31_0.png)
    



```python
ta.plot_added_vs_release_kde_boundary()
```


    
![png](https://raw.githubusercontent.com/thorwhalen/sung/main/misc/playlist_analysis_files/playlist_analysis_32_0.png)
    


### Plot First Letter Distribution


```python
ta.plot_first_letter_distribution(sort_by='lexicographical')
```


    
![png](https://raw.githubusercontent.com/thorwhalen/sung/main/misc/playlist_analysis_files/playlist_analysis_34_0.png)
    



```python
ta.plot_first_letter_distribution(sort_by='count')
```


    
![png](https://raw.githubusercontent.com/thorwhalen/sung/main/misc/playlist_analysis_files/playlist_analysis_35_0.png)
    


### Print Top Tracks by Starting Letter


```python
ta.print_top_names_by_letter(n=5)
```

    L (5 tracks):
      - (74) Levitating
      - (73) Livin' la Vida Loca
      - (63) Lucy In The Sky With Diamonds - Remastered 2009
      - (58) La Vie en rose
      - (50) Lose Yourself
    W (5 tracks):
      - (78) Wrecking Ball
      - (71) We Don't Talk About Bruno
      - (69) Wellerman - Sea Shanty
      - (69) We Will Rock You - Remastered 2011
      - (64) Wuthering Heights
    T (5 tracks):
      - (79) Tainted Love
      - (74) Training Season
      - (70) The Other Side
      - (70) The Greatest Show
      - (70) This Is Me
    H (5 tracks):
      - (82) Here Comes The Sun - Remastered 2009
      - (74) Happy Together
      - (57) Houdini
      - (57) Houdini
      - (57) Holocaust
    S (5 tracks):
      - (83) Sweet Dreams (Are Made of This) - 2005 Remaster
      - (75) Symphony (feat. Zara Larsson)
      - (74) Somebody That I Used To Know
      - (74) Señorita
      - (71) Super Trouper
    N (4 tracks):
      - (78) New Rules
      - (74) Nice For What
      - (63) Night Falls
      - (44) Non, je ne regrette rien
    R (5 tracks):
      - (77) Rolling in the Deep
      - (77) Roar
      - (70) Rewrite The Stars
      - (59) Ring My Bell
      - (48) Running Out Of Time
    E (4 tracks):
      - (90) Espresso
      - (83) exes
      - (77) Easy On Me
      - (53) Eating the Cats (Donald Trump Remix)
    A (5 tracks):
      - (73) Ain't Nobody (Loves Me Better) (feat. Jasmine Thompson)
      - (72) A Million Dreams
      - (53) A Spoonful of Sugar - From "Mary Poppins" / Soundtrack Version
      - (0) Anything You Can Do
      - (29) Away We Go
    1 (1 tracks):
      - (19) 10:35
    I (5 tracks):
      - (68) I Like To Move It
      - (66) Illusion
      - (65) I'll Be There for You - Theme From "Friends"
      - (47) It's Oh So Quiet
      - (40) Indiana Jones Theme
    C (5 tracks):
      - (69) Chandelier
      - (67) Come Alive
      - (62) Crab Rave
      - (53) Coconut
      - (46) Cups - Movie Version
    V (1 tracks):
      - (25) Viens
    U (1 tracks):
      - (14) Unity
    D (5 tracks):
      - (72) Don't Stop Believin'
      - (66) Dance Monkey
      - (62) Drive My Car - Remastered 2009
      - (53) Do-Re-Mi
      - (41) Don't Rain on My Parade
    M (5 tracks):
      - (74) MIDDLE OF THE NIGHT
      - (56) Material Girl
      - (49) Mellow Yellow
      - (46) Monster
      - (36) My Baby Just Cares For Me
    B (5 tracks):
      - (81) Before You Go
      - (81) bad guy
      - (76) bellyache
      - (74) bury a friend
      - (67) Bad - 2012 Remaster
    F (4 tracks):
      - (70) From Now On
      - (65) Friend Like Me
      - (63) Fat Bottomed Girls - Remastered 2011
      - (58) Fever
    G (5 tracks):
      - (74) Ghostbusters
      - (73) Get Into It (Yuh)
      - (72) Gangnam Style (강남스타일)
      - (62) Get Back Up Again
      - (59) Greased Lightnin' - From “Grease”
    P (3 tracks):
      - (64) Peaches
      - (30) Pink Panther Theme - Remix Version
      - (0) Papaoutai
    Y (3 tracks):
      - (65) You Can't Always Get What You Want
      - (49) You Can't Stop The Beat
      - (31) You're No Good - From 'Minions: The Rise of Gru' Soundtrack
    Z (1 tracks):
      - (82) Zombie
    K (3 tracks):
      - (77) Kings & Queens
      - (58) Karma Chameleon
      - (0) Kung Fu Fighting (From "Kung Fu Panda 3")
    O (5 tracks):
      - (64) Oye Como Va
      - (43) One Of A Kind
      - (41) On My Way
      - (40) One More Song
      - (0) Omg - Radio Edit
    J (3 tracks):
      - (75) Jolene
      - (43) Je Me Suis Fait Tout Petit
      - (33) Jolie coquine
    5 (1 tracks):
      - (30) 5:55
    . (1 tracks):
      - (81) ...Baby One More Time
    " (1 tracks):
      - (3) "Ellens Gesang III", D839: Ave Maria



```python
# To print all of them, just make n really big
ta.print_top_names_by_letter(n=10_000)
```

    L (12 tracks):
      - (74) Levitating
      - (73) Livin' la Vida Loca
      - (63) Lucy In The Sky With Diamonds - Remastered 2009
      - (58) La Vie en rose
      - (50) Lose Yourself
      - (47) Love The Way You Lie
      - (47) Le café
      - (44) Les cités d'or
      - (39) Little Boxes
      - (35) Lost and Found
      - (34) Lemon Boy - Acappella Version
      - (33) Laisse aller
    W (17 tracks):
      - (78) Wrecking Ball
      - (71) We Don't Talk About Bruno
      - (69) We Will Rock You - Remastered 2011
      - (69) Wellerman - Sea Shanty
      - (64) Wuthering Heights
      - (64) Who Let The Dogs Out
      - (48) What Time Is It
      - (46) Without Me
      - (43) West Side Story: Act I: America
      - (35) West Side Story: Act I: Something's Coming
      - (34) West Side Story: Act II: I Feel Pretty
      - (32) We the #Legends
      - (30) We Play All Night Long
      - (22) Winter Ducks Play on Water
      - (6) Waka Waka (This Time for Africa) [The Official 2010 FIFA World Cup (TM) Song] (feat. Freshlyground)
      - (0) Windy (Re-Recorded)
      - (0) Wimoweh (Mbube)
    T (16 tracks):
      - (79) Tainted Love
      - (74) Training Season
      - (70) The Other Side
      - (70) The Greatest Show
      - (70) This Is Me
      - (68) Truth Hurts
      - (67) Try Everything
      - (66) The Family Madrigal
      - (57) True Colors - Film Version
      - (56) The Magic Key
      - (54) The Real Slim Shady
      - (48) Time Alone With You (feat. Daniel Caesar)
      - (37) The Bare Necessities
      - (39) The Lonely Goatherd
      - (37) The Bare Necessities
      - (0) The Imperial March (Darth Vader's Theme)
    H (8 tracks):
      - (82) Here Comes The Sun - Remastered 2009
      - (74) Happy Together
      - (57) Houdini
      - (57) Houdini
      - (57) Holocaust
      - (31) Here Comes The Sun (feat. dodie)
      - (26) Hello
      - (0) Hello Song
    S (21 tracks):
      - (83) Sweet Dreams (Are Made of This) - 2005 Remaster
      - (75) Symphony (feat. Zara Larsson)
      - (74) Señorita
      - (74) Somebody That I Used To Know
      - (71) Super Trouper
      - (70) Solo (feat. Demi Lovato)
      - (68) Scatman (ski-ba-bop-ba-dop-bop)
      - (68) Somewhere Over The Rainbow_What A Wonderful World
      - (68) Surface Pressure
      - (65) Single Ladies (Put a Ring on It)
      - (46) Somebody That I Used to Know
      - (46) Somebody That I Used to Know
      - (36) Scarborough Fair / Canticle - Extended Version
      - (36) Strawberry Fields Forever - Remastered 2009
      - (30) Shape of You
      - (26) Stay Shrimpy
      - (24) Superman March - Alternate Version
      - (24) Sing, Sing, Sing
      - (18) Senza un perchè
      - (0) Suite No.3 In D Major, BWV 1068: 2. Air
      - (0) She Sells Sea Shells
    N (4 tracks):
      - (78) New Rules
      - (74) Nice For What
      - (63) Night Falls
      - (44) Non, je ne regrette rien
    R (8 tracks):
      - (77) Rolling in the Deep
      - (77) Roar
      - (70) Rewrite The Stars
      - (59) Ring My Bell
      - (48) Running Out Of Time
      - (47) Running with the Wolves - WolfWalkers Version
      - (23) Running Outta Love (feat. Tori Kelly)
      - (0) Ridin' in the Car
    E (4 tracks):
      - (90) Espresso
      - (83) exes
      - (77) Easy On Me
      - (53) Eating the Cats (Donald Trump Remix)
    A (8 tracks):
      - (73) Ain't Nobody (Loves Me Better) (feat. Jasmine Thompson)
      - (72) A Million Dreams
      - (53) A Spoonful of Sugar - From "Mary Poppins" / Soundtrack Version
      - (0) Anything You Can Do
      - (29) Away We Go
      - (28) All Norris Nuts Songs About Themselves
      - (2) Alors On Danse - Radio Edit
      - (0) Anything You Can Do
    1 (1 tracks):
      - (19) 10:35
    I (9 tracks):
      - (68) I Like To Move It
      - (66) Illusion
      - (65) I'll Be There for You - Theme From "Friends"
      - (47) It's Oh So Quiet
      - (40) Indiana Jones Theme
      - (35) I Wan'na Be Like You (2016)
      - (34) In My Bones (feat. Kimbra & Tank and The Bangas)
      - (11) I Got You - 1964 Smash Version
      - (0) It's Only A Paper Moon
    C (8 tracks):
      - (69) Chandelier
      - (67) Come Alive
      - (62) Crab Rave
      - (53) Coconut
      - (46) Cups - Movie Version
      - (36) C'est de l'eau
      - (22) Chill Jazz
      - (0) Coco Made Me Do It
    V (1 tracks):
      - (25) Viens
    U (1 tracks):
      - (14) Unity
    D (13 tracks):
      - (72) Don't Stop Believin'
      - (66) Dance Monkey
      - (62) Drive My Car - Remastered 2009
      - (53) Do-Re-Mi
      - (41) Don't Rain on My Parade
      - (38) Drop It Like It's Hot - Radio Edit
      - (37) Do The Bartman
      - (35) Dramophone
      - (25) Drive My Car
      - (11) Djevojka Sa Čardaš Nogama
      - (4) Do Your Ears Hang Low?
      - (1) Dragostea Din Tei
      - (0) Duel Of The Fates
    M (9 tracks):
      - (74) MIDDLE OF THE NIGHT
      - (56) Material Girl
      - (49) Mellow Yellow
      - (46) Monster
      - (36) My Baby Just Cares For Me
      - (30) My Own Drum (Remix) [with Missy Elliott]
      - (27) Malambo No. 1
      - (10) Mah Na Mah Na
      - (2) Mozart: Horn Concerto No. 4 in E-Flat Major, K. 495: III. Rondo (Allegro vivace)
    B (9 tracks):
      - (81) Before You Go
      - (81) bad guy
      - (76) bellyache
      - (74) bury a friend
      - (67) Bad - 2012 Remaster
      - (60) Blood on the Dance Floor
      - (46) Blue (Da Ba Dee)
      - (40) Bizet: Carmen, WD 31, Act 1: Habanera. "L'amour est un oiseau rebelle" (Carmen, Chœur)
      - (39) Baby Mine
    F (4 tracks):
      - (70) From Now On
      - (65) Friend Like Me
      - (63) Fat Bottomed Girls - Remastered 2011
      - (58) Fever
    G (7 tracks):
      - (74) Ghostbusters
      - (73) Get Into It (Yuh)
      - (72) Gangnam Style (강남스타일)
      - (62) Get Back Up Again
      - (59) Greased Lightnin' - From “Grease”
      - (40) Grand Finale
      - (32) Ghost in the Keys
    P (3 tracks):
      - (64) Peaches
      - (30) Pink Panther Theme - Remix Version
      - (0) Papaoutai
    Y (3 tracks):
      - (65) You Can't Always Get What You Want
      - (49) You Can't Stop The Beat
      - (31) You're No Good - From 'Minions: The Rise of Gru' Soundtrack
    Z (1 tracks):
      - (82) Zombie
    K (3 tracks):
      - (77) Kings & Queens
      - (58) Karma Chameleon
      - (0) Kung Fu Fighting (From "Kung Fu Panda 3")
    O (6 tracks):
      - (64) Oye Como Va
      - (43) One Of A Kind
      - (41) On My Way
      - (40) One More Song
      - (0) Omg - Radio Edit
      - (0) ooh la la (feat. Greg Nice & DJ Premier)
    J (3 tracks):
      - (75) Jolene
      - (43) Je Me Suis Fait Tout Petit
      - (33) Jolie coquine
    5 (1 tracks):
      - (30) 5:55
    . (1 tracks):
      - (81) ...Baby One More Time
    " (1 tracks):
      - (3) "Ellens Gesang III", D839: Ave Maria


### The dates table

Just a table with the added_at and album_release dates, along with other metadata, for convenience


```python
ta.dates
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
      <th>album_release_date</th>
      <th>added_at_date</th>
      <th>name</th>
      <th>first_artist</th>
      <th>name_and_artist</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>181</th>
      <td>2010-06-18</td>
      <td>2024-11-06</td>
      <td>Love The Way You Lie</td>
      <td>Eminem</td>
      <td>Love The Way You Lie -- Eminem</td>
    </tr>
    <tr>
      <th>180</th>
      <td>2002-05-26</td>
      <td>2024-11-03</td>
      <td>Without Me</td>
      <td>Eminem</td>
      <td>Without Me -- Eminem</td>
    </tr>
    <tr>
      <th>179</th>
      <td>2014-11-24</td>
      <td>2024-11-03</td>
      <td>Lose Yourself</td>
      <td>Eminem</td>
      <td>Lose Yourself -- Eminem</td>
    </tr>
    <tr>
      <th>178</th>
      <td>2005-12-06</td>
      <td>2024-11-03</td>
      <td>The Real Slim Shady</td>
      <td>Eminem</td>
      <td>The Real Slim Shady -- Eminem</td>
    </tr>
    <tr>
      <th>177</th>
      <td>2024-05-30</td>
      <td>2024-11-03</td>
      <td>Houdini</td>
      <td>Eminem</td>
      <td>Houdini -- Eminem</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2011-01-01</td>
      <td>2016-09-07</td>
      <td>Mah Na Mah Na</td>
      <td>Mahna Mahna and The Two Snowths</td>
      <td>Mah Na Mah Na -- Mahna Mahna and The Two Snowths</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2012-10-29</td>
      <td>2016-09-07</td>
      <td>Sing, Sing, Sing</td>
      <td>The Andrews Sisters</td>
      <td>Sing, Sing, Sing -- The Andrews Sisters</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2007-01-01</td>
      <td>2016-09-07</td>
      <td>My Baby Just Cares For Me</td>
      <td>Nina Simone</td>
      <td>My Baby Just Cares For Me -- Nina Simone</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2015-01-28</td>
      <td>2016-08-14</td>
      <td>Wimoweh (Mbube)</td>
      <td>Yma Sumac</td>
      <td>Wimoweh (Mbube) -- Yma Sumac</td>
    </tr>
    <tr>
      <th>0</th>
      <td>1997-01-01</td>
      <td>2016-08-14</td>
      <td>The Imperial March (Darth Vader's Theme)</td>
      <td>John Williams</td>
      <td>The Imperial March (Darth Vader's Theme) -- Jo...</td>
    </tr>
  </tbody>
</table>
<p>182 rows × 5 columns</p>
</div>




```python
ta.tracks_grouped_by_year
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
      <th>name_and_artist</th>
      <th>number_of_songs</th>
    </tr>
    <tr>
      <th>album_release_year</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1954</th>
      <td>[Malambo No. 1 -- Moises Vivanco]</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1961</th>
      <td>[West Side Story: Act II: I Feel Pretty -- Leo...</td>
      <td>3</td>
    </tr>
    <tr>
      <th>1965</th>
      <td>[The Lonely Goatherd -- Julie Andrews, Do-Re-M...</td>
      <td>3</td>
    </tr>
    <tr>
      <th>1967</th>
      <td>[Lucy In The Sky With Diamonds - Remastered 20...</td>
      <td>3</td>
    </tr>
    <tr>
      <th>1968</th>
      <td>[Scarborough Fair / Canticle - Extended Versio...</td>
      <td>2</td>
    </tr>
    <tr>
      <th>1969</th>
      <td>[You Can't Always Get What You Want -- The Rol...</td>
      <td>2</td>
    </tr>
    <tr>
      <th>1970</th>
      <td>[Oye Como Va -- Santana]</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1971</th>
      <td>[Coconut -- Harry Nilsson]</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1973</th>
      <td>[Strawberry Fields Forever - Remastered 2009 -...</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1974</th>
      <td>[Jolene -- Dolly Parton]</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1977</th>
      <td>[We Will Rock You - Remastered 2011 -- Queen]</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1978</th>
      <td>[Greased Lightnin' - From “Grease” -- John Tra...</td>
      <td>3</td>
    </tr>
    <tr>
      <th>1980</th>
      <td>[Super Trouper -- ABBA]</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1981</th>
      <td>[Tainted Love -- Soft Cell]</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1983</th>
      <td>[Les cités d'or -- Le Groupe Apollo, Sweet Dre...</td>
      <td>2</td>
    </tr>
    <tr>
      <th>1984</th>
      <td>[Material Girl -- Madonna]</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1988</th>
      <td>[Drive My Car -- Bobby McFerrin]</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1989</th>
      <td>[Je Me Suis Fait Tout Petit -- Georges Brassen...</td>
      <td>2</td>
    </tr>
    <tr>
      <th>1990</th>
      <td>[Do The Bartman -- The Simpsons]</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1991</th>
      <td>[Mozart: Horn Concerto No. 4 in E-Flat Major, ...</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1993</th>
      <td>[Somewhere Over The Rainbow_What A Wonderful W...</td>
      <td>2</td>
    </tr>
    <tr>
      <th>1994</th>
      <td>[Zombie -- The Cranberries]</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1995</th>
      <td>[Scatman (ski-ba-bop-ba-dop-bop) -- Scatman Jo...</td>
      <td>3</td>
    </tr>
    <tr>
      <th>1996</th>
      <td>[It's Only A Paper Moon -- Ella Fitzgerald]</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1997</th>
      <td>[Blood on the Dance Floor -- Michael Jackson, ...</td>
      <td>3</td>
    </tr>
    <tr>
      <th>1999</th>
      <td>[Livin' la Vida Loca -- Ricky Martin, Anything...</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2000</th>
      <td>[Indiana Jones Theme -- John Williams, Who Let...</td>
      <td>3</td>
    </tr>
    <tr>
      <th>2001</th>
      <td>[Don't Stop Believin' -- Journey]</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2002</th>
      <td>[Without Me -- Eminem, Dragostea Din Tei -- O-...</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2004</th>
      <td>[Drop It Like It's Hot - Radio Edit -- Snoop D...</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2005</th>
      <td>[The Real Slim Shady -- Eminem, Winter Ducks P...</td>
      <td>6</td>
    </tr>
    <tr>
      <th>2006</th>
      <td>[Pink Panther Theme - Remix Version -- Henry M...</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2007</th>
      <td>[What Time Is It -- Zac Efron, You Can't Stop ...</td>
      <td>8</td>
    </tr>
    <tr>
      <th>2008</th>
      <td>[C'est de l'eau -- Les Enfantastiques, I Like ...</td>
      <td>6</td>
    </tr>
    <tr>
      <th>2010</th>
      <td>[Love The Way You Lie -- Eminem, Waka Waka (Th...</td>
      <td>3</td>
    </tr>
    <tr>
      <th>2011</th>
      <td>[Rolling in the Deep -- Adele, Lost and Found ...</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2012</th>
      <td>[Gangnam Style (강남스타일) -- PSY, Somebody That I...</td>
      <td>6</td>
    </tr>
    <tr>
      <th>2013</th>
      <td>[Roar -- Katy Perry, Wrecking Ball -- Miley Cy...</td>
      <td>5</td>
    </tr>
    <tr>
      <th>2014</th>
      <td>[Lose Yourself -- Eminem, I Got You - 1964 Sma...</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2015</th>
      <td>[Cups - Movie Version -- Anna Kendrick, Unity ...</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2016</th>
      <td>[Chill Jazz -- Simon Leonard Thorpe, Ghostbust...</td>
      <td>10</td>
    </tr>
    <tr>
      <th>2017</th>
      <td>[New Rules -- Dua Lipa, The Other Side -- Hugh...</td>
      <td>14</td>
    </tr>
    <tr>
      <th>2018</th>
      <td>[Solo (feat. Demi Lovato) -- Clean Bandit, We ...</td>
      <td>6</td>
    </tr>
    <tr>
      <th>2019</th>
      <td>[We Play All Night Long -- Norris Nuts, Viens ...</td>
      <td>14</td>
    </tr>
    <tr>
      <th>2020</th>
      <td>[All Norris Nuts Songs About Themselves -- Nor...</td>
      <td>10</td>
    </tr>
    <tr>
      <th>2021</th>
      <td>[Stay Shrimpy -- Norris Nuts, Monster -- YOASO...</td>
      <td>14</td>
    </tr>
    <tr>
      <th>2022</th>
      <td>[Don't Rain on My Parade -- Lea Michele, Laiss...</td>
      <td>3</td>
    </tr>
    <tr>
      <th>2023</th>
      <td>[10:35 -- Tiësto, exes -- Tate McRae, Houdini ...</td>
      <td>5</td>
    </tr>
    <tr>
      <th>2024</th>
      <td>[Houdini -- Eminem, Eating the Cats (Donald Tr...</td>
      <td>5</td>
    </tr>
  </tbody>
</table>
</div>




```python

```

# Play with more playlists now


```python
from sung import TracksAnalysis

liked_songs_as_of_nov_2024 = "https://open.spotify.com/playlist/0TR0PpkMt37afbzNuexYEc?si=4ba4ec8221d84e94"

ta = TracksAnalysis(liked_songs_as_of_nov_2024)
```


```python
ta.plot_dataframe_distributions()
```


    
![png](https://raw.githubusercontent.com/thorwhalen/sung/main/misc/playlist_analysis_files/playlist_analysis_45_0.png)
    



```python
ta.plot_features_pairs()
```


    
![png](https://raw.githubusercontent.com/thorwhalen/sung/main/misc/playlist_analysis_files/playlist_analysis_46_0.png)
    



```python

```


