import os
from pathlib import Path
import ssl
import base64
import json
import subprocess

import requests
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from spotipy.exceptions import SpotifyException


class TLS12HttpAdapter(HTTPAdapter):
    """HTTPS adapter that forces TLS 1.2 for problematic middleboxes/AV proxies."""

    def __init__(self, *args, **kwargs):
        self._ssl_context = ssl.create_default_context()
        self._ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        self._ssl_context.maximum_version = ssl.TLSVersion.TLSv1_2
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = self._ssl_context
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs["ssl_context"] = self._ssl_context
        return super().proxy_manager_for(*args, **kwargs)


def _build_retry_session() -> requests.Session:
    """Create a requests session with retries for transient Spotify/network issues."""
    session = requests.Session()
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=0.6,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset({"GET", "POST"}),
        raise_on_status=False,
    )
    force_tls12 = os.environ.get("SPOTIFY_GET_FORCE_TLS12", "1").strip().lower() not in {
        "0",
        "false",
        "no",
        "off",
    }
    https_adapter = TLS12HttpAdapter(max_retries=retry) if force_tls12 else HTTPAdapter(max_retries=retry)
    http_adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", https_adapter)
    session.mount("http://", http_adapter)
    return session

def build_client() -> spotipy.Spotify:
    """Create an authenticated Spotify client."""
    # Try loading .env from current directory, then home directory
    load_dotenv()  # Current directory
    load_dotenv(Path.home() / ".env")  # Home directory
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError(
            "Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables.\n"
            "You can either:\n"
            "  1. Set them as environment variables in your shell\n"
            "  2. Create a .env file in your home directory (~/.env) or current directory\n"
            "     with: SPOTIFY_CLIENT_ID=... and SPOTIFY_CLIENT_SECRET=..."
        )
    session = _build_retry_session()
    auth_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret,
        requests_session=session,
        requests_timeout=20,
    )
    return spotipy.Spotify(
        auth_manager=auth_manager,
        requests_session=session,
        requests_timeout=20,
        retries=5,
        status_retries=5,
        backoff_factor=0.6,
    )


def _curl_json(method: str, url: str, headers: dict | None = None, data: str | None = None):
    """Call an HTTPS endpoint through curl.exe (Windows schannel) and parse JSON."""
    cmd = ["curl.exe", "-sS", "--fail-with-body", "--max-time", "30", "-X", method, url]
    for k, v in (headers or {}).items():
        cmd.extend(["-H", f"{k}: {v}"])
    if data is not None:
        cmd.extend(["--data", data])

    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"curl request failed for {url}: {detail}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON response from {url}: {result.stdout[:500]}") from exc


def _get_spotify_creds() -> tuple[str, str]:
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError("Spotify credentials are missing (SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET).")
    return client_id, client_secret


def _spotify_token_curl() -> str:
    client_id, client_secret = _get_spotify_creds()
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("ascii")
    payload = _curl_json(
        "POST",
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data="grant_type=client_credentials",
    )
    token = payload.get("access_token")
    if not token:
        raise RuntimeError(f"Could not get Spotify access token via curl fallback: {payload}")
    return token


def _fetch_tracks_curl(playlist: str):
    token = _spotify_token_curl()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/playlists/{playlist}/tracks?limit=100&offset=0"
    tracks = []

    while url:
        payload = _curl_json("GET", url, headers=headers)
        for item in payload.get("items", []):
            track = item.get("track") or {}
            name = track.get("name")
            if not name:
                continue
            artists = ", ".join(artist.get("name", "") for artist in track.get("artists", []))
            tracks.append((artists, name, None))
        url = payload.get("next")

    return tracks


def _fetch_track_curl(track_id: str):
    token = _spotify_token_curl()
    payload = _curl_json(
        "GET",
        f"https://api.spotify.com/v1/tracks/{track_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    name = payload.get("name")
    if not name:
        return []
    artists = ", ".join(artist.get("name", "") for artist in payload.get("artists", []))
    return [(artists, name)]


def fetch_tracks(sp_client: spotipy.Spotify, playlist: str):
    """Return list of (artists, name) tuples for the given playlist."""
    try:
        results = sp_client.playlist_tracks(playlist)
    except requests.exceptions.SSLError as exc:
        print(
            "Python TLS handshake to Spotify failed; trying Windows curl fallback..."
        )
        try:
            return _fetch_tracks_curl(playlist)
        except Exception as fallback_exc:
            raise RuntimeError(
                "Could not establish a secure TLS connection to Spotify from Python, and curl fallback also failed.\n"
                "This is usually a local network/SSL issue (VPN/proxy/antivirus TLS inspection, bad clock, or ISP filtering).\n"
                f"Fallback error: {fallback_exc}"
            ) from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            "Spotify network request failed. Check your internet connection, proxy settings, and firewall rules."
        ) from exc
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
    except requests.exceptions.SSLError as exc:
        print(
            "Python TLS handshake to Spotify failed; trying Windows curl fallback..."
        )
        try:
            return _fetch_track_curl(track_id)
        except Exception as fallback_exc:
            raise RuntimeError(
                "Could not establish a secure TLS connection to Spotify from Python, and curl fallback also failed.\n"
                "This is usually a local network/SSL issue (VPN/proxy/antivirus TLS inspection, bad clock, or ISP filtering).\n"
                f"Fallback error: {fallback_exc}"
            ) from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            "Spotify network request failed. Check your internet connection, proxy settings, and firewall rules."
        ) from exc
    except SpotifyException as exc:
        # Gracefully handle missing/invalid track IDs
        print(f"Failed to fetch track {track_id}: {exc}")
        return []
    name = track.get("name")
    if not name:
        return []
    artists = ", ".join(artist["name"] for artist in track.get("artists", []))
    return [(artists, name)]