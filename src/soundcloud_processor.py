import json, subprocess

def soundcloud_entries(playlist_url: str, cookies_from_browser: str = None, cookies_file: str = None):
    cmd = ["yt-dlp", "-J", "--flat-playlist"]
    if cookies_from_browser:
        cmd.extend(["--cookies-from-browser", cookies_from_browser])
    elif cookies_file:
        cmd.extend(["--cookies", cookies_file])
    cmd.append(playlist_url)
    
    proc = subprocess.run(
        cmd,
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


def get_soundcloud_title(url: str, cookies_from_browser: str = None, cookies_file: str = None) -> str:
  """
  Get the title of a SoundCloud track.

  Args:
    url: The URL of the SoundCloud track.
    cookies_from_browser: Browser to extract cookies from (e.g., chrome, firefox, edge).
    cookies_file: Path to cookies file (Netscape format).
  Returns:
    The title of the SoundCloud track.
  """
  cmd = ["yt-dlp", "-J", "--no-playlist"]
  if cookies_from_browser:
      cmd.extend(["--cookies-from-browser", cookies_from_browser])
  elif cookies_file:
      cmd.extend(["--cookies", cookies_file])
  cmd.append(url)
  
  proc = subprocess.run(
      cmd,
      capture_output=True,
      text=True,
      check=True,
  )
  return json.loads(proc.stdout).get("title")