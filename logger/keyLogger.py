from pynput import keyboard

def on_press(key):
    """
    Callback function invoked when a key is pressed.
    """
    try:
        # print alphanumeric keys
        print(f'Key pressed: {key.char}')
    except AttributeError:
        # print special keys (e.g., ctrl, alt, enter)
        print(f'Special key pressed: {key}')

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