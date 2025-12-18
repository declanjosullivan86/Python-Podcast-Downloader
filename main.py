import requests
import feedparser
import re
import sys
import os
import subprocess
from tqdm import tqdm

def sanitize_filename(filename):
    """
    Removes characters that are invalid in filenames and truncates for safety.
    """
    # Remove invalid characters (\ / : * ? " < > |)
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Replace sequences of whitespace or hyphens with a single underscore
    sanitized = re.sub(r'[\s-]+', '_', sanitized)
    sanitized = sanitized.strip('_')
    return sanitized[:200]

def fetch_feed(url):
    """
    Fetches and parses the RSS feed using feedparser.
    """
    print(f"Fetching feed from: {url} ...")
    try:
        feed = feedparser.parse(url)
        if not feed.entries:
            print("Error: No episodes found in this feed.", file=sys.stderr)
            return None
        return feed
    except Exception as e:
        print(f"An error occurred while fetching the feed: {e}", file=sys.stderr)
        return None

def display_episodes(feed):
    """
    Displays the podcast title and a numbered list of episodes.
    """
    if not feed or not feed.feed:
        return
        
    print("\n" + "="*70)
    print(f"Podcast: {feed.feed.title}")
    print(f"Total Episodes Available: {len(feed.entries)}")
    print("="*70 + "\n")
    
    entries = feed.entries
    total = len(entries)
    display_limit = 5
    
    def print_range(ep_list, start_index):
        for i, entry in enumerate(ep_list):
            pub_date = entry.get('published', 'No date')
            print(f"  [{start_index + i + 1:03}] {entry.title} ({pub_date})")

    if total <= display_limit * 2:
        print_range(entries, 0)
    else:
        print_range(entries[:display_limit], 0)
        print(f"  ... ({total - 2 * display_limit} episodes hidden) ...")
        print_range(entries[-display_limit:], total - display_limit)
    print("\n") 

def get_audio_enclosure(entry):
    """
    Finds the best audio enclosure URL. Returns (url, is_opus)
    """
    if 'enclosures' not in entry:
        return None, False

    # Check for native Opus/Ogg first
    for enclosure in entry.enclosures:
        mime = enclosure.get('type', '')
        if 'opus' in mime or 'ogg' in mime:
            return enclosure.get('href'), True
    
    # Fallback to MP3
    for enclosure in entry.enclosures:
        mime = enclosure.get('type', '')
        if 'mpeg' in mime or 'mp3' in mime:
            return enclosure.get('href'), False
                
    return None, False

def convert_to_opus(input_path, output_path):
    """
    Uses FFmpeg to convert an MP3 file to Opus.
    """
    print(f"Transcoding {input_path} to Opus...")
    try:
        # We use subprocess to call ffmpeg directly. 
        # -y: overwrite output
        # -i: input file
        # -c:a libopus: use opus codec
        # -b:a 64k: set bitrate (Opus is very efficient at 64k)
        command = [
            'ffmpeg', '-y', '-i', input_path, 
            '-c:a', 'libopus', '-b:a', '64k', 
            output_path
        ]
        # Run command and hide output unless there is an error
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        return True
    except FileNotFoundError:
        print("Error: FFmpeg not found. Please install FFmpeg to use transcoding features.", file=sys.stderr)
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error during transcoding: {e}", file=sys.stderr)
        return False

def download_episode(entry):
    """
    Downloads the selected episode. Transcodes to Opus if source is MP3.
    """
    audio_url, is_native_opus = get_audio_enclosure(entry)
    
    if not audio_url:
        print(f"Skipping '{entry.title}': No supported audio URL found.", file=sys.stderr)
        return

    base_name = sanitize_filename(entry.title)
    final_filename = f"{base_name}.opus"
    
    if os.path.exists(final_filename):
        print(f"File already exists, skipping: {final_filename}")
        return

    # If it's not native opus, we download to a temporary mp3 file first
    download_filename = final_filename if is_native_opus else f"{base_name}.tmp.mp3"

    print(f"\nDownloading '{entry.title}'...")
    try:
        with requests.get(audio_url, stream=True, timeout=30) as r:
            r.raise_for_status() 
            total_size = int(r.headers.get('content-length', 0))
            
            with open(download_filename, 'wb') as f, tqdm(
                total=total_size, unit='iB', unit_scale=True, desc="Download"
            ) as pbar:
                for data in r.iter_content(8192):
                    f.write(data)
                    pbar.update(len(data))
            
        # Transcode if necessary
        if not is_native_opus:
            success = convert_to_opus(download_filename, final_filename)
            if os.path.exists(download_filename):
                os.remove(download_filename) # Clean up temp file
            if success:
                print(f"Successfully transcoded: {final_filename}")
        else:
            print(f"Successfully downloaded: {final_filename}")
                
    except Exception as e:
        print(f"\nAn error occurred: {e}", file=sys.stderr)
        if not is_native_opus and os.path.exists(download_filename):
            os.remove(download_filename)

def parse_range_input(user_input, total_episodes):
    """
    Parses user input into a list of 0-based indices.
    """
    user_input = user_input.strip().lower().replace(' ', '')
    try:
        if user_input == 'all':
            return list(range(total_episodes)), None
        elif user_input.startswith('f'):
            match = re.search(r'f(\d+)', user_input)
            if match:
                return list(range(min(int(match.group(1)), total_episodes))), None
        elif user_input.startswith('l'):
            match = re.search(r'l(\d+)', user_input)
            if match:
                n = int(match.group(1))
                return list(range(max(0, total_episodes - n), total_episodes)), None
        elif '-' in user_input:
            start, end = map(int, user_input.split('-'))
            if 1 <= start <= end <= total_episodes:
                return list(range(start - 1, end)), None
        else:
            idx = int(user_input)
            if 1 <= idx <= total_episodes:
                return [idx - 1], None
    except:
        pass
    return [], "Invalid selection format."

def main():
    print("--- Python Podcast Downloader (Auto-Transcode to Opus) ---")
    url = input("Enter podcast RSS feed URL (or press Enter for default): \n[https://feeds.podcastindex.org/pc20.xml]: ")
    url = url if url else 'https://feeds.podcastindex.org/pc20.xml'
    
    feed = fetch_feed(url)
    if not feed: sys.exit(1)
        
    display_episodes(feed)
    total = len(feed.entries)
    
    while True:
        choice = input(f"Enter selection (1-{total}, fN, lN, all, or q to quit): ").strip().lower()
        if choice == 'q': break
        
        indices, error = parse_range_input(choice, total)
        if error:
            print(f"Error: {error}")
            continue

        for index in indices:
            try:
                download_episode(feed.entries[index])
            except KeyboardInterrupt:
                sys.exit(0)
        print("\n--- Process finished ---")

if __name__ == "__main__":
    main()
