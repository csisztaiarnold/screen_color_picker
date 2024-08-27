import tkinter as tk
from tkinter import messagebox
from pynput import keyboard, mouse
from PIL import ImageGrab, Image, ImageTk, ImageDraw
import threading
import pyautogui
import pystray
from pystray import MenuItem as item
from PIL import Image as PILImage

icon = None


def get_hex(rgb):
    return '%02X%02X%02X' % rgb


def check_color(x, y):
    try:
        if root.winfo_containing(x, y) is not None:
            return
    except KeyError:
        pass
    bbox = (x, y, x + 1, y + 1)
    im = ImageGrab.grab(bbox=bbox)
    rgbim = im.convert('RGB')
    r, g, b = rgbim.getpixel((0, 0))
    rgb = f'rgb({r}, {g}, {b})'
    hex_color = f'#{get_hex((r, g, b))}'
    rgb_entry.delete(0, tk.END)
    rgb_entry.insert(0, rgb)
    hex_entry.delete(0, tk.END)
    hex_entry.insert(0, hex_color)
    color_box.config(bg=hex_color)


def update_zoomed_image():
    while True:
        x, y = root.winfo_pointerxy()
        bbox = (x - 5, y - 5, x + 5, y + 5)
        im = ImageGrab.grab(bbox=bbox)
        im = im.resize((430, 340), Image.NEAREST)

        draw = ImageDraw.Draw(im)
        center_x, center_y = 236, 187
        draw.line((center_x - 10, center_y, center_x + 10, center_y), fill="red", width=1)
        draw.line((center_x, center_y - 10, center_x, center_y + 10), fill="red", width=1)

        img = ImageTk.PhotoImage(im)
        zoomed_label.config(image=img)
        zoomed_label.image = img


def move_mouse(key):
    x, y = pyautogui.position()
    if key == keyboard.Key.up:
        pyautogui.moveTo(x, y - 1)
    elif key == keyboard.Key.down:
        pyautogui.moveTo(x, y + 1)
    elif key == keyboard.Key.left:
        pyautogui.moveTo(x - 1, y)
    elif key == keyboard.Key.right:
        pyautogui.moveTo(x + 1)
    elif key == keyboard.Key.space:
        check_color(x, y)


def on_press(key):
    try:
        move_mouse(key)
    except AttributeError:
        pass


def start_keyboard_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


def copy_to_clipboard(entry):
    root.clipboard_clear()
    root.clipboard_append(entry.get())
    messagebox.showinfo("Copy to clipboard", "Color value copied to clipboard!")


def minimize_to_tray():
    root.withdraw()
    image = PILImage.open("icon.png")
    menu = (item('Restore', restore_from_tray), item('Quit', quit_app))
    icon = pystray.Icon("color_picker", image, "Screen Color Picker", menu)
    icon.run()


def restore_from_tray(icon, item):
    icon.stop()
    root.deiconify()


def quit_app(icon, item):
    icon.stop()
    root.quit()


def main():
    global root, rgb_entry, hex_entry, zoomed_label, color_box
    root = tk.Tk()
    root.title("Screen Color Picker")
    root.geometry("450x460")
    root.attributes('-topmost', True)
    root.resizable(False, False)

    tk.Label(root, text="RGB:").grid(row=0, column=0, padx=10, pady=10)
    rgb_entry = tk.Entry(root)
    rgb_entry.grid(row=0, column=1, padx=10, pady=10)
    rgb_copy_button = tk.Button(root, text="Copy", command=lambda: copy_to_clipboard(rgb_entry))
    rgb_copy_button.grid(row=0, column=2, padx=10, pady=10)

    color_box = tk.Label(root, width=10, height=1)
    color_box.grid(row=0, column=3, padx=10, pady=10)

    tk.Label(root, text="HEX:").grid(row=1, column=0, padx=10, pady=10)
    hex_entry = tk.Entry(root)
    hex_entry.grid(row=1, column=1, padx=10, pady=10)
    hex_copy_button = tk.Button(root, text="Copy", command=lambda: copy_to_clipboard(hex_entry))
    hex_copy_button.grid(row=1, column=2, padx=10, pady=10)

    zoomed_label = tk.Label(root)
    zoomed_label.grid(row=2, column=0, columnspan=4, padx=10, pady=10)

    shrink_image = ImageTk.PhotoImage(file="minimize.png")
    shrink_button = tk.Button(root, image=shrink_image, command=minimize_to_tray)
    shrink_button.grid(row=1, column=3, padx=10, pady=10)

    threading.Thread(target=update_zoomed_image, daemon=True).start()
    threading.Thread(target=start_keyboard_listener, daemon=True).start()

    root.mainloop()


if __name__ == '__main__':
    main()
