Spotify playlist/track downloader CLI. It looks up tracks on YouTube (via `yt-dlp`) and downloads audio.

## Setup
- Python 3.9+ recommended.
- Install deps: `pip install -r requirements.txt` (or via package install below).
- Provide Spotify API creds:
  - Create a `.env` file in the project (kept out of git):
    ```
    SPOTIFY_CLIENT_ID=your_spotify_client_id
    SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
    ```
  - Or set them in your shell profile so they’re always available.
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
