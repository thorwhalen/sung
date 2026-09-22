# sung.tools

Tools using sung

### Functions

| [`get_content_bytes`](#sung.tools.get_content_bytes)(key[, max_age, ...])         | Get bytes of content from `thorwhalen/content`, automatically caching locally.   |
|-------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| `get_github_table`(key[, max_age, ...])                                                         |                                                                                  |
| [`raw_github_url`](#sung.tools.raw_github_url)([path, repo_stub, branch, ...]) | Return the raw github url for a given path in a given repo and branch.           |

### Classes

| `TracksAnalysis`(playlist)   |    |
|------------------------------|----|

### sung.tools.get_content_bytes(key, max_age=None, \*, cache_locally=False, content_url=<function raw_github_url>)

Get bytes of content from `thorwhalen/content`, automatically caching locally.

```text
# add max_age=1e-6 if you want to update the data with the remote data
b = get_content_bytes('tables/csv/projects.csv', max_age=None)
```

### sung.tools.raw_github_url(path=None, , repo_stub='thorwhalen/sung_content', branch=None, url_prefix='https://raw.githubusercontent.com')

Return the raw github url for a given path in a given repo and branch.

By default, the repo_stub is ‘thorwhalen/sung_content’ and the branch is ‘main’.

```pycon
>>> raw_github_url('parquet/greatest_500_songs.parquet')
'https://raw.githubusercontent.com/thorwhalen/sung_content/main/parquet/greatest_500_songs.parquet'
```

If the path is not given, return a partial function that takes the path as argument.
That is, will make a “path to url” function for a given repo and branch.

```pycon
>>> get_url = raw_github_url(repo_stub='thorwhalen/content', branch='master')
>>> get_url('tables/csv/named_urls.csv')
'https://raw.githubusercontent.com/thorwhalen/content/master/tables/csv/named_urls.csv'
```
