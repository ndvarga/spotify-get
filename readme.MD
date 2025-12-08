Spotify playlist/track downloader CLI. It looks up tracks on YouTube (via `yt-dlp`) and downloads audio.

## Setup
- Python 3.9+ recommended.
- Install system deps: `pip install -r requirements.txt`.
- Put Spotify API creds in `src/spotify_secrets.py`:
  ```python
  CLIENT_ID = "your_spotify_client_id"
  CLIENT_SECRET = "your_spotify_client_secret"
  ```
- Install the CLI (from repo root):
  - Editable: `python -m pip install -e .`
  - Regular: `python -m pip install .`
  This exposes the `spotify-dl` command on your PATH.

## Usage
CLI entry point (works from any directory after install):
```
spotify-dl <playlist_url_or_id> [options]
spotify-dl --track <track_url_or_id> [options]
```

Options:
- `-f, --audio-format` (default `mp3`): audio format for `yt-dlp`.
- `-o, --output` (default `downloads`): directory where files are saved.
- `-t, --threads` (default `4`): max concurrent downloads.

Examples:
```
# Download a Spotify playlist
spotify-dl https://open.spotify.com/playlist/your_id

# Download a single Spotify track
spotify-dl --track https://open.spotify.com/track/your_id

# SoundCloud playlist or track
spotify-dl https://soundcloud.com/playlist-url
spotify-dl --track https://soundcloud.com/track-url

# Custom format/output and concurrency
spotify-dl https://open.spotify.com/playlist/your_id -f m4a -o downloads -t 6
```

Notes:
- Output template: `<output>/<title>.<ext>` as resolved by `yt-dlp`.
- Spotify lookups search YouTube via `ytsearch:<artist> <title>`.
