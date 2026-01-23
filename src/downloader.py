import sys
import subprocess
import os
import shutil

def download_song(source: str, audio_format: str, output_template: str, artists: str = None, name: str = None, url:str = None, cookies_from_browser: str = None, cookies_file: str = None, list_formats: bool = False, verbose: bool = False):
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
  if list_formats:
    # List formats for debugging
    cmd_parts = ['yt-dlp', '--list-formats']
    if verbose:
      cmd_parts.append('--verbose')
    
    # Add cookies and other options for format listing
    if cookies_from_browser:
      browser = cookies_from_browser.lower()
      cmd_parts.extend(['--cookies-from-browser', browser])
      print(f"Using cookies from browser: {browser}")
    elif cookies_file:
      if not os.path.exists(cookies_file):
        print(f"ERROR: Cookies file not found: {cookies_file}")
        sys.exit(1)
      cmd_parts.extend(['--cookies', cookies_file])
      print(f"Using cookies file: {cookies_file}")
    
    cmd_parts.extend(['--retries', '10', '--fragment-retries', '10'])
    
    if source == "spotify":
      cmd_parts.extend(['--remote-components', 'ejs:github'])
      deno_path = shutil.which('deno')
      if not deno_path:
        winget_deno_path = os.path.expanduser(
          r"~\AppData\Local\Microsoft\WinGet\Packages\DenoLand.Deno_Microsoft.Winget.Source_8wekyb3d8bbwe\deno.exe"
        )
        if os.path.exists(winget_deno_path):
          deno_path = winget_deno_path
          cmd_parts.extend(['--js-runtimes', f'deno:{deno_path}'])
        else:
          winget_packages = os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Packages")
          if os.path.exists(winget_packages):
            for item in os.listdir(winget_packages):
              if item.startswith('DenoLand.Deno'):
                potential_deno = os.path.join(winget_packages, item, 'deno.exe')
                if os.path.exists(potential_deno):
                  deno_path = potential_deno
                  cmd_parts.extend(['--js-runtimes', f'deno:{deno_path}'])
                  break
      if deno_path and '--js-runtimes' not in cmd_parts:
        cmd_parts.extend(['--js-runtimes', 'deno'])
      
      cmd_parts.extend([
        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        '--referer', 'https://www.youtube.com/'
      ])
    
    cmd_parts.append(query)
    
    if cookies_from_browser or cookies_file:
      print(f"Running: yt-dlp [with cookies] {' '.join(cmd_parts[1:len(cmd_parts)-1])} [query]")
    
    result = subprocess.run(cmd_parts, check=False, capture_output=True, text=True)
    
    if result.stdout:
      print(result.stdout, end='')
    if result.stderr:
      print(result.stderr, end='', file=sys.stderr)
    
    sys.stdout.flush()
    sys.stderr.flush()
    
    error_output = result.stderr + result.stdout
    result_code = result.returncode
  else:
    # For audio extraction, try formats individually in order of preference
    # Start with audio-only https formats, then fallback to others
    # Format priority: audio-only https > audio-only m3u8 > video+audio https > video+audio m3u8
    format_selectors = [
      'bestaudio[protocol!=m3u8]',  # Audio-only https (251, 250, 249, 140)
      'bestaudio',                   # Any audio-only format
      'best[acodec!=none][protocol!=m3u8]',  # Video+audio https (18, etc)
      'best[acodec!=none]'           # Any format with audio
    ]
    
    # Validate cookies file if provided
    if cookies_file and not os.path.exists(cookies_file):
      print(f"ERROR: Cookies file not found: {cookies_file}")
      sys.exit(1)
    
    # Try each format selector until one works
    last_error = None
    result_code = 1
    for fmt_selector in format_selectors:
      cmd_parts = ['yt-dlp', '-x', '--embed-metadata', '--audio-format', audio_format,
                   '--format', fmt_selector,
                   '-o', output_template]
      if verbose:
        cmd_parts.append('--verbose')
      
      # Add cookies and other options (same for all attempts)
      if cookies_from_browser:
        browser = cookies_from_browser.lower()
        cmd_parts.extend(['--cookies-from-browser', browser])
        if fmt_selector == format_selectors[0]:  # Only print once
          print(f"Using cookies from browser: {browser}")
      elif cookies_file:
        cmd_parts.extend(['--cookies', cookies_file])
        if fmt_selector == format_selectors[0]:  # Only print once
          print(f"Using cookies file: {cookies_file}")
      
      cmd_parts.extend(['--retries', '10', '--fragment-retries', '10'])
      
      if source == "spotify":
        cmd_parts.extend(['--remote-components', 'ejs:github'])
        deno_path = shutil.which('deno')
        if not deno_path:
          winget_deno_path = os.path.expanduser(
            r"~\AppData\Local\Microsoft\WinGet\Packages\DenoLand.Deno_Microsoft.Winget.Source_8wekyb3d8bbwe\deno.exe"
          )
          if os.path.exists(winget_deno_path):
            deno_path = winget_deno_path
            cmd_parts.extend(['--js-runtimes', f'deno:{deno_path}'])
            if fmt_selector == format_selectors[0]:  # Only print once
              print(f"Found Deno at winget location: {deno_path}")
          else:
            winget_packages = os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Packages")
            if os.path.exists(winget_packages):
              for item in os.listdir(winget_packages):
                if item.startswith('DenoLand.Deno'):
                  potential_deno = os.path.join(winget_packages, item, 'deno.exe')
                  if os.path.exists(potential_deno):
                    deno_path = potential_deno
                    cmd_parts.extend(['--js-runtimes', f'deno:{deno_path}'])
                    if fmt_selector == format_selectors[0]:  # Only print once
                      print(f"Found Deno at: {deno_path}")
                    break
        if deno_path and '--js-runtimes' not in cmd_parts:
          cmd_parts.extend(['--js-runtimes', 'deno'])
        
        cmd_parts.extend([
          '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          '--referer', 'https://www.youtube.com/'
        ])
      
      cmd_parts.append(query)
      
      if fmt_selector != format_selectors[0]:  # Don't print for first attempt
        print(f"\nTrying fallback format selector: {fmt_selector}")
      
      if verbose:
        # Print full command in verbose mode
        print(f"[DEBUG] Running command: {' '.join(cmd_parts)}")
      elif cookies_from_browser or cookies_file:
        print(f"Running: yt-dlp [with cookies] {' '.join(cmd_parts[1:len(cmd_parts)-1])} [query]")
      
      # Run the download attempt
      result = subprocess.run(cmd_parts, check=False, capture_output=True, text=True)
      
      # Print output
      if result.stdout:
        print(result.stdout, end='')
      if result.stderr:
        print(result.stderr, end='', file=sys.stderr)
      
      sys.stdout.flush()
      sys.stderr.flush()
      
      # If successful, we're done
      if result.returncode == 0:
        return  # Success!
      
      # Check if it's a 403 error - if so, try next format
      error_output = result.stderr + result.stdout
      if "403" in error_output or "Forbidden" in error_output:
        last_error = error_output
        print(f"\nFormat selector '{fmt_selector}' failed with 403, trying next format...")
        continue  # Try next format
      else:
        # Different error, break and show error message
        last_error = error_output
        result_code = result.returncode
        break
    
    # If we get here, all formats failed - handle error below
    error_output = last_error or ""
  
  # Detect specific error types
  format_error = "Requested format is not available" in error_output or "Only images are available" in error_output
  sabr_error = "SABR streaming" in error_output or "challenge solving failed" in error_output
  ejs_error = "challenge solving failed" in error_output or "JavaScript runtime" in error_output or "EJS" in error_output
  
  # Note: DPAPI errors will be visible in the output above
  # We'll provide helpful messages based on return code and common patterns
  
  # If download failed, provide helpful error messages
  if result_code != 0:
    if source == "spotify":
      if cookies_from_browser:
        browser_lower = cookies_from_browser.lower()
        print("\n" + "="*60)
        if browser_lower in ['chrome', 'chromium']:
          print("ERROR: Chrome cookie decryption failed (DPAPI error on Windows)")
          print("\nThis is a known Windows issue with Chrome cookies.")
          print("SOLUTIONS (in order of recommendation):")
          print("1. Use Firefox instead: --cookies-from-browser firefox")
          print("   (Firefox doesn't have this DPAPI issue on Windows)")
          print("2. Use Edge: --cookies-from-browser edge")
          print("3. Manually export cookies from Chrome:")
          print("   - Install 'Get Cookies.txt LOCALLY' browser extension")
          print("   - Go to youtube.com and export cookies")
          print("   - Use: --cookies /path/to/cookies.txt")
        else:
          if format_error:
            print("ERROR: Format not available - This is a format selection issue, not a cookie issue.")
            print("\nThe video might:")
            print("  - Only have video formats (no separate audio stream)")
            print("  - Be a YouTube Short with limited format options")
            print("  - Have region/age restrictions affecting format availability")
            print("\nSOLUTIONS:")
            print("1. Update yt-dlp (most important):")
            print("   pip install --upgrade yt-dlp")
            print("2. Try a different search result (the video might have format issues)")
            print("3. The format selection has been improved in the code")
          else:
            print("Download failed even with cookies. Try these solutions:")
            print("1. Close your browser completely before running the command")
            print("2. Make sure you're logged into YouTube in that browser")
            print("   - Open Firefox, go to youtube.com, and make sure you're logged in")
            print("   - Watch a video to ensure your session is active")
            print("3. Update yt-dlp: pip install --upgrade yt-dlp")
            print("4. Try manually exporting cookies:")
            print("   - Install 'Get Cookies.txt LOCALLY' extension in Firefox")
            print("   - Go to youtube.com and export cookies")
            print("   - Use: --cookies /path/to/cookies.txt")
            print("5. The video might be region-restricted, age-restricted, or require special access")
            print("6. Try waiting a few minutes - YouTube may be rate-limiting your IP")
        print("="*60)
      elif cookies_file:
        print("\n" + "="*60)
        if ejs_error:
          print("ERROR: EJS (External JS Scripts) challenge solving failed")
          print("\nYouTube requires JavaScript challenge solving. Even with Deno installed, you need:")
          print("1. Deno in your PATH (verify with: deno --version)")
          print("2. EJS challenge solver scripts installed")
          print("\nSOLUTIONS:")
          print("1. Verify Deno is installed and in PATH:")
          print("   deno --version")
          print("   (If this fails, restart your terminal or add Deno to PATH)")
          print("2. Install yt-dlp with default dependencies (includes EJS scripts):")
          print("   pip install -U \"yt-dlp[default]\"")
          print("   This installs both yt-dlp and yt-dlp-ejs package")
          print("3. Or install EJS scripts manually:")
          print("   pip install yt-dlp-ejs")
          print("4. The code uses --remote-components ejs:github to auto-download scripts")
          print("   If GitHub is blocked, use option 2 or 3 above")
          print("5. Try explicitly enabling Deno:")
          print("   The code should auto-detect Deno, but if it doesn't work,")
          print("   you may need to restart your terminal after installing Deno")
          print("\nSee: https://github.com/yt-dlp/yt-dlp/wiki/EJS for full setup guide")
        elif sabr_error:
          print("ERROR: YouTube SABR streaming / Challenge solving issue detected")
          print("\nYouTube is forcing SABR streaming which requires JavaScript challenge solving.")
          print("The code now uses 'android' player client to avoid this issue.")
          print("\nSOLUTIONS:")
          print("1. The player client has been changed from 'web' to 'android'")
          print("   (This should avoid SABR streaming issues)")
          print("2. If it still fails, try installing JavaScript runtime:")
          print("   pip install pyexecjs")
          print("3. Update yt-dlp: pip install --upgrade yt-dlp")
          print("4. Try a different search result")
        elif format_error:
          print("ERROR: Format not available - This is a format selection issue, not a cookie issue.")
          print("\nThe video might:")
          print("  - Only have video formats (no separate audio stream)")
          print("  - Be a YouTube Short with limited format options")
          print("  - Have region/age restrictions affecting format availability")
          print("\nSOLUTIONS:")
          print("1. Update yt-dlp (most important):")
          print("   pip install --upgrade yt-dlp")
          print("2. Try a different search result (the video might have format issues)")
          print("3. The player client has been changed to 'android' to avoid SABR issues")
        else:
          print("Download failed. The cookies file might be expired or invalid.")
          print("\nTROUBLESHOOTING:")
          print("1. Re-export cookies (they expire quickly):")
          print("   - Go to youtube.com in your browser")
          print("   - Make sure you're logged in")
          print("   - Use 'Get Cookies.txt LOCALLY' extension to export fresh cookies")
          print("2. Make sure the cookies file is in Netscape format")
          print("3. Try using --cookies-from-browser firefox instead")
          print("4. Update yt-dlp: pip install --upgrade yt-dlp")
        print("="*60)
      else:
        print("\nDownload failed. This may be due to YouTube blocking requests.")
        print("Try running with: --cookies-from-browser chrome")
        print("Or: --cookies-from-browser firefox")