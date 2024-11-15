# sung

Music data access. Mainly sources from spotify and wikipedia.


# Install

To install:	```pip install sung```

For most tools, you'll also need a spotify

```
export SPOTIFY_API_CLIENT_ID="your_api_client_id"
export SPOTIFY_API_CLIENT_SECRET="your_api_client_secrete"
export SPOTIPY_REDIRECT_URI="http://localhost:8000/callback"
export SPOTIPY_CLIENT_ID="$SPOTIFY_API_CLIENT_ID"
export SPOTIPY_CLIENT_SECRET="$SPOTIFY_API_CLIENT_SECRET"
```

## Spotify API credentials?

To obtain Spotify API credentials, follow these steps:
	1.	Create a Spotify Developer Account:
	•	Visit the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
	•	Log in with your Spotify account or create a new one.
	2.	Register a New Application:
	•	Click on “Create an App.”
	•	Provide an App Name and App Description.
	•	Agree to the Developer Terms of Service.
	•	Click “Create.”
	3.	Retrieve Client ID and Client Secret:
	•	After creating the app, you’ll be directed to the app’s dashboard.
	•	Here, you’ll find your Client ID and Client Secret.
	•	Keep these credentials secure; they are essential for API authentication.
	4.	Set Redirect URIs (if applicable):
	•	In your app settings, click “Edit Settings.”
	•	Under “Redirect URIs,” add the URIs where Spotify should redirect after authentication.
	•	This is crucial for certain authorization flows.

For detailed information on authorization flows and using your credentials, refer to 
[Spotify’s Authorization Guide](https://developer.spotify.com/documentation/web-api/concepts/authorization).

Ensure you handle your Client Secret securely and adhere to 
[Spotify’s Developer Terms of Service](https://developer.spotify.com/terms/).


# Examples


## search_tracks

```python
>>> from sung import search_tracks
>>> search_tracks('Autumn leaves', limit=3, genre='jazz')  # doctest: +ELLIPSIS
```



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
      <th>disc_number</th>
      <th>external_ids</th>
      <th>external_urls</th>
      <th>href</th>
      <th>is_local</th>
      <th>track_number</th>
      <th>type</th>
      <th>uri</th>
      <th>preview_url</th>
      <th>added_at_datetime</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>181</th>
      <td>Love The Way You Lie</td>
      <td>Eminem</td>
      <td>263373</td>
      <td>47</td>
      <td>False</td>
      <td>2010-06-18</td>
      <td>2010</td>
      <td>2024-11-06</td>
      <td>https://open.spotify.com/track/4k5Rb51qsUSMFg6...</td>
      <td>L</td>
      <td>...</td>
      <td>1</td>
      <td>{'isrc': 'USUM71015443'}</td>
      <td>{'spotify': 'https://open.spotify.com/track/4k...</td>
      <td>https://api.spotify.com/v1/tracks/4k5Rb51qsUSM...</td>
      <td>False</td>
      <td>15</td>
      <td>track</td>
      <td>spotify:track:4k5Rb51qsUSMFg6oFdVC48</td>
      <td>NaN</td>
      <td>2024-11-06T16:01:38Z</td>
    </tr>
    <tr>
      <th>180</th>
      <td>Without Me</td>
      <td>Eminem</td>
      <td>290120</td>
      <td>46</td>
      <td>False</td>
      <td>2002-05-26</td>
      <td>2002</td>
      <td>2024-11-03</td>
      <td>https://open.spotify.com/track/3Q0kSmKpkffn4aW...</td>
      <td>W</td>
      <td>...</td>
      <td>1</td>
      <td>{'isrc': 'USIR10211127'}</td>
      <td>{'spotify': 'https://open.spotify.com/track/3Q...</td>
      <td>https://api.spotify.com/v1/tracks/3Q0kSmKpkffn...</td>
      <td>False</td>
      <td>10</td>
      <td>track</td>
      <td>spotify:track:3Q0kSmKpkffn4aWkYkWwet</td>
      <td>NaN</td>
      <td>2024-11-03T11:27:58Z</td>
    </tr>
    <tr>
      <th>179</th>
      <td>Lose Yourself</td>
      <td>Eminem</td>
      <td>320573</td>
      <td>50</td>
      <td>False</td>
      <td>2014-11-24</td>
      <td>2014</td>
      <td>2024-11-03</td>
      <td>https://open.spotify.com/track/2jvHb9SHJDi8Ugk...</td>
      <td>L</td>
      <td>...</td>
      <td>2</td>
      <td>{'isrc': 'USIR10211570'}</td>
      <td>{'spotify': 'https://open.spotify.com/track/2j...</td>
      <td>https://api.spotify.com/v1/tracks/2jvHb9SHJDi8...</td>
      <td>False</td>
      <td>3</td>
      <td>track</td>
      <td>spotify:track:2jvHb9SHJDi8Ugky7tUzUb</td>
      <td>NaN</td>
      <td>2024-11-03T11:27:34Z</td>
    </tr>
    <tr>
      <th>178</th>
      <td>The Real Slim Shady</td>
      <td>Eminem</td>
      <td>283693</td>
      <td>54</td>
      <td>False</td>
      <td>2005-12-06</td>
      <td>2005</td>
      <td>2024-11-03</td>
      <td>https://open.spotify.com/track/2WXUcFnJPPATncU...</td>
      <td>T</td>
      <td>...</td>
      <td>1</td>
      <td>{'isrc': 'USIR10000449'}</td>
      <td>{'spotify': 'https://open.spotify.com/track/2W...</td>
      <td>https://api.spotify.com/v1/tracks/2WXUcFnJPPAT...</td>
      <td>False</td>
      <td>9</td>
      <td>track</td>
      <td>spotify:track:2WXUcFnJPPATncUkPYC54v</td>
      <td>NaN</td>
      <td>2024-11-03T11:27:15Z</td>
    </tr>
    <tr>
      <th>177</th>
      <td>Houdini</td>
      <td>Eminem</td>
      <td>227239</td>
      <td>57</td>
      <td>False</td>
      <td>2024-05-30</td>
      <td>2024</td>
      <td>2024-11-03</td>
      <td>https://open.spotify.com/track/6vw2M02LT3otGUo...</td>
      <td>H</td>
      <td>...</td>
      <td>1</td>
      <td>{'isrc': 'USUG12403399'}</td>
      <td>{'spotify': 'https://open.spotify.com/track/6v...</td>
      <td>https://api.spotify.com/v1/tracks/6vw2M02LT3ot...</td>
      <td>False</td>
      <td>1</td>
      <td>track</td>
      <td>spotify:track:6vw2M02LT3otGUoK4ZqHwx</td>
      <td>NaN</td>
      <td>2024-11-03T11:21:18Z</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 25 columns</p>
</div>



## Perform Analyses


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



    
![png](https://raw.githubusercontent.com/thorwhalen/sung/main/misc/playlist_analysis_files/playlist_analysis_20_1.png)
    


### Plot Added Date vs. Release Date


```python
ta.plot_added_vs_release_dates()
```


    
![png](https://raw.githubusercontent.com/thorwhalen/sung/main/misc/playlist_analysis_files/playlist_analysis_22_0.png)
    



```python
ta.plot_added_vs_release_kde()
```


    
![png](https://raw.githubusercontent.com/thorwhalen/sung/main/misc/playlist_analysis_files/playlist_analysis_23_0.png)
    



```python
ta.plot_added_vs_release_kde_boundary()
```


    
![png](https://raw.githubusercontent.com/thorwhalen/sung/main/misc/playlist_analysis_files/playlist_analysis_24_0.png)
    


### Plot First Letter Distribution


```python
ta.plot_first_letter_distribution(sort_by='lexicographical')
```


    
![png](https://raw.githubusercontent.com/thorwhalen/sung/main/misc/playlist_analysis_files/playlist_analysis_26_0.png)
    



```python
ta.plot_first_letter_distribution(sort_by='count')
```


    
![png](https://raw.githubusercontent.com/thorwhalen/sung/main/misc/playlist_analysis_files/playlist_analysis_27_0.png)
    


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

