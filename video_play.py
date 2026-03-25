import os
import vlc
import time
import keyboard

# Point to your VLC install (64-bit recommended)
os.add_dll_directory(r"C:\Program Files\VideoLAN\VLC")


def play_playlist(videos):
    instance = vlc.Instance(
        "--quiet",
        "--log-verbose=0",
        "--width=400",
        "--height=250"
    )

    player = instance.media_player_new()

    index = 0
    paused = False

    def load_video(i):
        media = instance.media_new(videos[i])
        player.set_media(media)
        player.play()
        time.sleep(1)

    load_video(index)

    print("\nControls:")
    print("SPACE = pause/play")
    print("N = next video")
    print("B = previous video")
    print("Q = quit\n")

    while True:
        state = player.get_state()

        # Auto move to next when video ends
        if state == vlc.State.Ended:
            index += 1
            if index >= len(videos):
                print("Playlist finished.")
                break
            load_video(index)

        # Controls
        if keyboard.is_pressed("space"):
            player.pause()
            time.sleep(0.4)

        elif keyboard.is_pressed("n"):
            index += 1
            if index < len(videos):
                load_video(index)
            else:
                print("No next video")
                index -= 1
            time.sleep(0.4)

        elif keyboard.is_pressed("b"):
            index -= 1
            if index >= 0:
                load_video(index)
            else:
                print("No previous video")
                index = 0
            time.sleep(0.4)

        elif keyboard.is_pressed("q"):
            player.stop()
            break

        time.sleep(0.1)


# 🔥 Example usage
videos = [
    "Halsey - Without Me (Lyrics).mp4",
    "Rayvanny_Happy Birthday.mp3",
    "Rayvanny_Happy Birthday.mp4"
]

play_playlist(videos)