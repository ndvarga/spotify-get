import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# expects secrets.py in the same folder defining client_id and client_secret
from secrets import client_id, client_secret


def build_client() -> spotipy.Spotify:
    """Create an authenticated Spotify client."""
    return spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret,
        )
    )


def fetch_tracks(sp_client: spotipy.Spotify, playlist: str):
    """Return list of (artists, name) tuples for the given playlist."""
    results = sp_client.playlist_tracks(playlist)
    tracks = []

    while results:
        for item in results["items"]:
            track = item.get("track") or {}
            name = track.get("name")
            if not name:
                continue
            artists = ", ".join(artist["name"] for artist in track.get("artists", []))
            tracks.append((artists, name))
        if results.get("next"):
            results = sp_client.next(results)
        else:
            break

    return tracks


def download_song(artists: str, name: str, audio_format: str, output_template: str):
    os.system(
        f'yt-dlp -x --embed-metadata --audio-format {audio_format} '
        f'-o "{output_template}" '
        f'"ytsearch:{artists} {name}"'
    )
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(
        description="Download songs from a Spotify playlist using yt-dlp."
    )
    parser.add_argument(
        "playlist",
        help="Spotify playlist URL or ID",
    )
    parser.add_argument(
        "-s",
        "--save",
        help="Optional path to save track names to a .txt file",
    )
    parser.add_argument(
        "-f",
        "--audio-format",
        default="mp3",
        help="Audio format for yt-dlp (default: mp3)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="downloads",
        help="Directory to write downloaded audio files (default: downloads)",
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=4,
        help="Maximum number of concurrent downloads (default: 4)",
    )
    args = parser.parse_args()

    sp_client = build_client()
    tracks = fetch_tracks(sp_client, args.playlist)

    if not tracks:
        print("No tracks found.")
        return

    if args.save:
        Path(args.save).write_text("\n".join(f"{a} - {n}" for a, n in tracks), encoding="utf-8")
        print(f"Wrote track list to {args.save}")

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(output_dir / "%(title)s.%(ext)s")

    max_workers = max(1, args.threads)
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for artists, name in tracks:
            pool.submit(download_song, artists, name, args.audio_format, output_template)


if __name__ == "__main__":
    main()
