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