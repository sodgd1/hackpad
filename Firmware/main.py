import board
import busio
import time

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation

# OLED Display
try:
    import adafruit_ssd1306
    from PIL import Image, ImageDraw, ImageFont
    DISPLAY_AVAILABLE = True
except ImportError:
    DISPLAY_AVAILABLE = False

keyboard = KMKKeyboard()

# 2x2 matrix
keyboard.row_pins = (board.GP3, board.GP2)
keyboard.col_pins = (board.GP1, board.GP0)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

# OLED setup
if DISPLAY_AVAILABLE:
    i2c = busio.I2C(board.GP5, board.GP4)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3C)

    current_label = ""

    try:
        font = ImageFont.load_default()
    except:
        font = None

    def show_text(text):
        image = Image.new("1", (128, 32))  # 1-bit (better for OLED)
        draw = ImageDraw.Draw(image)

        # Get text size for centering
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (128 - text_width) // 2
        y = (32 - text_height) // 2

        draw.text((x, y), text, fill=255, font=font)

        oled.fill(0)
        oled.image(image)
        oled.show()

    # Hook keypress
    original_process_key = keyboard.process_key

    def new_process_key(key, is_pressed, int_coord):
        if is_pressed:
            if key == KC.MPLY:
                show_text("PLAY")
            elif key == KC.MNXT:
                show_text("NEXT")
            elif key == KC.MPRV:
                show_text("PREV")
            elif key == KC.MUTE:
                show_text("MUTE")

        return original_process_key(key, is_pressed, int_coord)

    keyboard.process_key = new_process_key

# Media keymap
keyboard.keymap = [
    [
        KC.MPLY, KC.MNXT,
        KC.MPRV, KC.MUTE
    ]
]

# Main
if __name__ == '__main__':
    if DISPLAY_AVAILABLE:
        oled.fill(0)
        oled.show()

    keyboard.go()
