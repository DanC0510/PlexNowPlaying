import requests
import xml.etree.ElementTree as ET
import time
import os
import keyboard
import json
import msvcrt

with open('credentials.json') as data_file:
    data = json.load(data_file)

PLEX_BASE = data['PLEX_BASE']
TOKEN = data['PLEX_TOKEN']

TEXT_FILE = "nowplaying.txt"
ART_FILE = "cover.jpg"

RUNNING = True

LAST_ART_URL = None

def clear_files():
    with open(TEXT_FILE, "w", encoding="utf-8") as f:
        f.write("")

    if os.path.exists(ART_FILE):
        try:
            os.remove(ART_FILE)
        except:
            pass

while RUNNING == True:
    if msvcrt.kbhit():
        key = msvcrt.getch()

        if key.lower() == b'e':
            RUNNING = False
            continue
            
    try:        
        url = f"{PLEX_BASE}/status/sessions?X-Plex-Token={TOKEN}"

        response = requests.get(url, timeout=5)

        root = ET.fromstring(response.text)

        track = root.find("Track")

        if track is not None:
            song = track.attrib.get("title", "")
            artist = track.attrib.get("grandparentTitle", "")
            album = track.attrib.get("parentTitle", "")

            display_text = f"{song} - {artist}          "

            # Write text for OBS
            with open(TEXT_FILE, "r", encoding="utf-8") as r:
                if r.read() != display_text:
                    with open(TEXT_FILE, "w", encoding="utf-8") as f:
                        f.write(display_text)

            print(display_text)

            # Album artwork
            thumb = track.attrib.get("thumb")

            if thumb:
                art_url = (
                    f"{PLEX_BASE}{thumb}"
                    f"?X-Plex-Token={TOKEN}"
                )

                # Only redownload if artwork changed
                if art_url != LAST_ART_URL:
                    art_response = requests.get(
                        art_url,
                        timeout=10
                    )

                    if art_response.status_code == 200:
                        with open(ART_FILE, "wb") as img:
                            img.write(art_response.content)

                        LAST_ART_URL = art_url
                        print("Updated album artwork")

        else:
            clear_files()
            LAST_ART_URL = None

    except Exception as e:
        print("Error:", e)


clear_files()
