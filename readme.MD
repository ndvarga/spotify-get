Spotify playlist downloader CLI that searches each track on YouTube via `yt-dlp`, downloads audio, and can optionally write the track list to a text file.

## Setup
- Python 3.9+ recommended.
- Install `yt-dlp` on your PATH: `pip install yt-dlp` (inside your venv).
- Install Python deps: `pip install -r requirements.txt`.
- Create `secrets.py` in the repo root with your Spotify app credentials:
  ```python
  client_id = "your_spotify_client_id"
  client_secret = "your_spotify_client_secret"
  ```

## Usage
Run from the project root:
```
python song_from_playlist.py <playlist_url_or_id> [options]
```

Options:
- `-f, --audio-format` (default `mp3`): audio format passed to `yt-dlp`.
- `-o, --output` (default `downloads`): directory where files are saved.
- `-t, --threads` (default `4`): max concurrent downloads.
- `-s, --save` (optional): path to write track names (one per line).

Examples:
```
# Basic download
python song_from_playlist.py https://open.spotify.com/playlist/your_id

# Custom format/output and limited concurrency
python song_from_playlist.py https://open.spotify.com/playlist/your_id \
  -f m4a -o downloads -t 6

# Save track list to a file
python song_from_playlist.py https://open.spotify.com/playlist/your_id \
  --save tracks.txt
```

Notes:
- Downloads use the template `<output>/<title>.<ext>` as resolved by `yt-dlp`.
- The script searches YouTube (`ytsearch:`) using track artist/name from Spotify.
