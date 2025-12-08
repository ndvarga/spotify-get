import os
import sys

def download_song(source: str, audio_format: str, output_template: str, artists: str = None, name: str = None, url:str = None):
  """
  Download a song from YouTube or SoundCloud using yt-dlp.
  
  Args:
    source: The source of the song.
    audio_format: The audio format to download the song in.
    output_template: The template to use for the output file.
    artists: The artists of the song.
    name: The name of the song.
    url: The URL of the song.
  """
  if source == "spotify":
    query = f"ytsearch:{artists} {name}"
  elif source == "soundcloud":
    query = url
  else:
    raise ValueError(f"Invalid source: {source}")
  os.system(
      f'yt-dlp -x --embed-metadata --audio-format {audio_format} '
      f'-o "{output_template}" '
      f'"{query}"'
  )
  sys.stdout.flush()