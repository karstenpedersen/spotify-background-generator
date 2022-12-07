import ctypes
import io
import os
import random

import requests
from PIL import Image, ImageStat
from spotipy import Spotify, SpotifyOAuth

from env import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

# Settings
# "average", "blured", "grain", tuple for specific color
WALLPAPER_BACKGROUND_TYPE = "average"
WALLPAPER_BACKGROUND_WIDTH = 1920
WALLPAPER_BACKGROUND_HEIGHT = 1080
# Can be "none", "artist", "track", "artist-a-track"
WALLPAPER_DISPLAY_TRACK_INFO = "none"

WALLPAPER_FOLDER_PATH = r"C:\Users\Karsten Pedersen\Pictures\generated-album-wallpapers"

SPOTIFY_TYPE = "liked"  # Can be "liked", "playlist" or "artist"
SPOTIFY_QUERY_COUNT = 20
SPOTIFY_QUERY_OFFSET = 0

IMAGE_EXTENSIONS = [".png", ".jpg"]

SPI_SETDESKWALLPAPER = 20


def create_spotify_oauth() -> SpotifyOAuth:
    """Create SpotifyOAuth instance.

    Returns:
        SpotifyOAuth: Created SpotifyOAuth instance
    """
    return SpotifyOAuth(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope="user-library-read")


def image_from_url(url: str) -> Image:
    """Get PIL Image from url request.

    Args:
        url (str): Url to request from

    Returns:
        Image: Created image
    """
    image_data = requests.get(url).content
    image_bytes = io.BytesIO(image_data)
    image = Image.open(image_bytes)

    return image


def get_spotify_tracks(spotify: Spotify) -> list:
    tracks = []
    if SPOTIFY_TYPE == "liked":
        tracks = [item.get("track") for item in spotify.current_user_saved_tracks(
            SPOTIFY_QUERY_COUNT, SPOTIFY_QUERY_OFFSET).get("items")]

    return tracks


def create_album_wallpapers(spotify: Spotify) -> list[str]:
    """Create wallpaper images.

    Args:
        spotify (Spotify): Spotify

    Returns:
        list[str]: List of paths to created wallpapers
    """
    # Get liked tracks
    tracks = get_spotify_tracks(spotify)  # spotify.current_user_saved_tracks()

    wallpaper_paths = []

    for track in tracks:
        wallpaper_path = create_album_wallpaper(track)
        wallpaper_paths.append(wallpaper_path)

    return wallpaper_paths


def create_album_wallpaper(track: any) -> str:
    """Create wallpaper image from spotify track.

    Args:
        track (any): Spotify track

    Returns:
        str: Wallpaper image path
    """
    # Unpack item
    album = track.get("album")
    album_image = album.get("images")[0]

    # Unpack track info
    track_name = track.get("name")

    # Unpack and request image
    image_url = album_image.get("url")
    width = album_image.get("width")
    height = album_image.get("height")
    image = image_from_url(image_url)

    # Create wallpaper image
    if WALLPAPER_BACKGROUND_TYPE == "average":
        average_color = tuple(ImageStat.Stat(image).median)
    else:
        average_color = (0, 0, 0)

    wallpaper_image = Image.new(
        "RGB", (WALLPAPER_BACKGROUND_WIDTH, WALLPAPER_BACKGROUND_HEIGHT), average_color)

    # Paste album on background with offset
    offset = ((WALLPAPER_BACKGROUND_WIDTH - width) // 2,
              (WALLPAPER_BACKGROUND_HEIGHT - height) // 2)
    wallpaper_image.paste(image, offset)

    # Get absolute path to image
    wallpaper_path = os.path.abspath(
        f"{WALLPAPER_FOLDER_PATH}/{track_name}.png")

    # Save image
    wallpaper_image.save(wallpaper_path)

    return wallpaper_path


def is_image(path: str) -> bool:
    """Check if given path is to an image.

    Args:
        path (str): File path

    Returns:
        bool: Is image

    >>> is_image("backgrounds/test.png")
    True
    >>> is_image("backgrounds/test.jpg")
    True
    >>> is_image("backgrounds/test.pdf")
    False
    """
    for valid_extension in IMAGE_EXTENSIONS:
        if path.endswith(valid_extension):
            return True

    return False


def get_wallpaper_paths() -> list[str]:
    """Get wallpaper paths.

    Returns:
        list[str]: _description_
    """
    # Get directory path
    directory_path = os.path.abspath(WALLPAPER_FOLDER_PATH)

    # Get wallpaper paths
    wallpaper_paths = list(
        filter(lambda p: is_image(p), os.listdir(directory_path)))

    return wallpaper_paths


def get_random_wallpaper() -> str:
    """Get random wallpaper from WALLPAPER_FOLDER_PATH directory.

    Returns:
        str: Path
    """
    # Get wallpaper paths
    wallpaper_paths = get_wallpaper_paths()

    # Get wallpaper path
    wallpaper_path = random.choice(wallpaper_paths)

    return wallpaper_path


def set_wallpaper(wallpaper_path: str) -> None:
    """Set desktop wallpaper.

    Args:
        wallpaper_path (str): Path to image
    """
    # Set desktop wallpaper
    # Windows
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, wallpaper_path, 0)


def randomize_wallpaper(wallpaper_paths: list[str]) -> None:
    """Randomize desktop wallpaper.

    Args:
        wallpaper_paths (list[str]): Wallpaper paths to select from
    """
    # Select random wallpaper
    wallpaper_path = random.choice(wallpaper_paths)

    set_wallpaper(wallpaper_path)


if __name__ == "__main__":
    # Create backgrounds
    spotify = Spotify(auth_manager=create_spotify_oauth())
    wallpaper_paths = create_album_wallpapers(spotify)

    # Select random background
    randomize_wallpaper(wallpaper_paths)
