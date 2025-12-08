import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# expects secrets.py in the same folder defining client_id and client_secret
from secrets import CLIENT_ID, CLIENT_SECRET
from spotipy.exceptions import SpotifyException

def build_client() -> spotipy.Spotify:
    """Create an authenticated Spotify client."""
    return spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
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
            tracks.append((artists, name, None))
        if results.get("next"):
            results = sp_client.next(results)
        else:
            break

    return tracks


def fetch_track(sp_client: spotipy.Spotify, track_id: str):
    """Return list with a single (artists, name) tuple for a track."""
    try:
        track = sp_client.track(track_id) or {}
    except SpotifyException as exc:
        # Gracefully handle missing/invalid track IDs
        print(f"Failed to fetch track {track_id}: {exc}")
        return []
    name = track.get("name")
    if not name:
        return []
    artists = ", ".join(artist["name"] for artist in track.get("artists", []))
    return [(artists, name)]