import json, subprocess

def soundcloud_entries(playlist_url: str):
    proc = subprocess.run(
        ["yt-dlp", "-J", "--flat-playlist", playlist_url],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(proc.stdout)
    entries = data.get("entries") or []
    urls = []
    for e in entries:
        sc_id = e.get("id")
        if sc_id:
            urls.append(e.get("url") or f"https://soundcloud.com/{sc_id}")
    return urls


def get_soundcloud_title(url: str) -> str:
  """
  Get the title of a SoundCloud track.

  Args:
    url: The URL of the SoundCloud track.
  Returns:
    The title of the SoundCloud track.
  """
  proc = subprocess.run(
      ["yt-dlp", "-J", "--no-playlist", url],
      capture_output=True,
      text=True,
      check=True,
  )
  return json.loads(proc.stdout).get("title")