from pynput import keyboard
import re

url = "http://127.0.0.1:6000/api/trackSwipe/"

def on_press(key):
    """
    Callback function invoked when a key is pressed.
    """

    banned_words = ["FRICK", "STINKY"]

    try:
        # print alphanumeric keys
        keystrokes += {f'{key.char}'}
        if (any(word.capitalize in keystrokes for word in banned_words)):
            payload = {
                "flagged_word": word,
            }
            response = requests.post(url, json=payload)
    except AttributeError:
        # print special keys (e.g., ctrl, alt, enter)
        print(f'{key}')

def on_release(key):
    """
    Callback function invoked when a key is released.
    """
    # Stop the listener if the Escape key is pressed
    if key == keyboard.Key.esc:
        print("Exiting listener...")
        return False

# Collect events until released
print("Listening for keyboard input. Press 'Esc' to stop.")
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()