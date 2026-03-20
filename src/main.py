import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from downloader import download_song
from spotify_client import build_client, fetch_tracks, fetch_track
from soundcloud_processor import get_soundcloud_title, soundcloud_entries


def main():
    parser = argparse.ArgumentParser(
        description="Download songs from a Spotify playlist using yt-dlp."
    )
    parser.add_argument(
        "playlist",
        nargs="?",
        help="Playlist URL or ID",
    )
    parser.add_argument(
        "-r",
        "--track",
        help="Track URL or ID (single-track download)",
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
    parser.add_argument(
        "--cookies-from-browser",
        help="Browser to extract cookies from (e.g., chrome, firefox, edge, safari). More reliable than --cookies for YouTube.",
    )
    parser.add_argument(
        "--cookies",
        help="Path to cookies file (Netscape format). Export using 'Get Cookies.txt LOCALLY' browser extension. Use --cookies-from-browser for automatic extraction.",
    )
    parser.add_argument(
        "--list-formats",
        action="store_true",
        help="List available formats for debugging instead of downloading.",
    )
    parser.add_argument(
        "--yt-player-client",
        default="default,tv,ios",
        help="YouTube player clients for yt-dlp extractor args (default: default,tv,ios).",
    )
    parser.add_argument(
        "--yt-po-token",
        help="Optional YouTube PO token (e.g., mweb.gvs+TOKEN) for formats requiring GVS PO token.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose/debug output for yt-dlp and other operations.",
    )
    args = parser.parse_args()

    if not args.playlist and not args.track:
        parser.error("provide a playlist URL/ID or --track URL/ID")

    tracks = []
    sp_client = None
    ext = args.audio_format.split(".")[-1]
    source = None

    if args.track:
        if "spotify.com" in args.track or args.track.startswith("spotify:track"):
            track_id = args.track.split("/")[-1].split("?")[0]
            try:
                sp_client = sp_client or build_client()
                tracks = fetch_track(sp_client, track_id)
            except RuntimeError as exc:
                print(exc)
                return
            source = "spotify"
            output_template = f"{args.output}/%(title)s.%(ext)s"
            download_song("spotify", args.audio_format, output_template, artists=tracks[0][0], name=tracks[0][1], cookies_from_browser=args.cookies_from_browser, cookies_file=args.cookies, list_formats=args.list_formats, verbose=args.verbose, yt_player_client=args.yt_player_client, yt_po_token=args.yt_po_token)
            return
        elif "soundcloud" in args.track:
            # direct download; no track list to process
            title = get_soundcloud_title(args.track, cookies_from_browser=args.cookies_from_browser, cookies_file=args.cookies)
            output_template = f"{args.output}/{title}.{ext}"
            download_song("soundcloud", args.audio_format, output_template, url=args.track, cookies_from_browser=args.cookies_from_browser, cookies_file=args.cookies, list_formats=args.list_formats, verbose=args.verbose, yt_player_client=args.yt_player_client, yt_po_token=args.yt_po_token)
            return

    if args.playlist:
        if "spotify.com" in args.playlist or args.playlist.startswith("spotify:playlist"):
            playlist_id = args.playlist.split("/")[-1].split("?")[0]
            try:
                sp_client = sp_client or build_client()
                tracks = fetch_tracks(sp_client, playlist_id)
            except RuntimeError as exc:
                print(exc)
                return
            source = "spotify"
        elif "soundcloud" in args.playlist:
            urls = soundcloud_entries(args.playlist, cookies_from_browser=args.cookies_from_browser, cookies_file=args.cookies)
            titles = [get_soundcloud_title(url, cookies_from_browser=args.cookies_from_browser, cookies_file=args.cookies) for url in urls]
            tracks = [("SoundCloud", title, url) for title, url in zip(titles, urls)]
            source = "soundcloud"
        else:
            parser.error("invalid playlist URL/ID")

    if not tracks:
        print("No tracks found.")
        return

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(output_dir / "%(title)s.%(ext)s")

    max_workers = max(1, args.threads)
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for artists, name, url in tracks:
            pool.submit(
                download_song,
                source,
                args.audio_format,
                output_template,
                artists,
                name,
                url if source == "soundcloud" else None,
                args.cookies_from_browser,
                args.cookies,
                args.list_formats,
                args.verbose,
                args.yt_player_client,
                args.yt_po_token,
            )


if __name__ == "__main__":
    main()
