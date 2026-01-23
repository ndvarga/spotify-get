import sys
import subprocess

def download_song(source: str, audio_format: str, output_template: str, artists: str = None, name: str = None, url:str = None, cookies_from_browser: str = None, cookies_file: str = None):
  """
  Download a song from YouTube or SoundCloud using yt-dlp.
  
  Args:
    source: The source of the song.
    audio_format: The audio format to download the song in.
    output_template: The template to use for the output file.
    artists: The artists of the song.
    name: The name of the song.
    url: The URL of the song.
    cookies_from_browser: Browser to extract cookies from (e.g., chrome, firefox, edge).
    cookies_file: Path to cookies file (Netscape format).
  """
  if source == "spotify":
    query = f"ytsearch:{artists} {name}"
  elif source == "soundcloud":
    query = url
  else:
    raise ValueError(f"Invalid source: {source}")
  
  # Build yt-dlp command
  cmd_parts = ['yt-dlp', '-x', '--embed-metadata', '--audio-format', audio_format, '-o', output_template]
  
  # Add cookies options if provided
  if cookies_from_browser:
    cmd_parts.extend(['--cookies-from-browser', cookies_from_browser])
  elif cookies_file:
    cmd_parts.extend(['--cookies', cookies_file])
  
  cmd_parts.append(query)
  
  # Use subprocess for better security and handling
  subprocess.run(cmd_parts, check=False)
  sys.stdout.flush()