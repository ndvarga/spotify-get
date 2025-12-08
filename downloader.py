import os
import sys

def download_song(artists: str, name: str, audio_format: str, output_template: str):
    os.system(
        f'yt-dlp -x --embed-metadata --audio-format {audio_format} '
        f'-o "{output_template}" '
        f'"ytsearch:{artists} {name}"'
    )
    sys.stdout.flush()