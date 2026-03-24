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

    wave_active = False
    wave_start_time = 0.0
    wave_duration = 0.5

    current_label = ""

    try:
        font = ImageFont.load_default()
    except:
        font = None

    def trigger_wave(label_text):
        global wave_active, wave_start_time, current_label
        wave_active = True
        wave_start_time = time.monotonic()
        current_label = label_text

    def render_wave():
        global wave_active

        image = Image.new("RGB", (128, 32), (0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw text
        if current_label:
            draw.text((5, 10), current_label, fill=(255, 255, 255), font=font)

        if wave_active:
            elapsed = time.monotonic() - wave_start_time

            if elapsed >= wave_duration:
                wave_active = False
            else:
                progress = elapsed / wave_duration
                wave_width = int(progress * 64)
                brightness = 255 * (1 - (progress)**2)

                center_x = 64

                if brightness > 20:
                    red = int(brightness)
                    color = (red, 0, 0)

                    for dx in range(wave_width):
                        x_left = center_x - dx
                        x_right = center_x + dx

                        if 0 <= x_left < 128:
                            draw.line([(x_left, 0), (x_left, 31)], fill=color)

                        if 0 <= x_right < 128:
                            draw.line([(x_right, 0), (x_right, 31)], fill=color)

        oled.image(image)
        oled.show()

    # Hook keypress
    original_process_key = keyboard.process_key

    def new_process_key(key, is_pressed, int_coord):
        if is_pressed:
            if key == KC.MPLY:
                trigger_wave("PLAY ⏸")
            elif key == KC.MNXT:
                trigger_wave("NEXT ⏭")
            elif key == KC.MPRV:
                trigger_wave("PREV ⏮")
            elif key == KC.MUTE:
                trigger_wave("MUTE 🔇")
        return original_process_key(key, is_pressed, int_coord)

    keyboard.process_key = new_process_key

# Media keymap
keyboard.keymap = [
    [
        KC.MPLY, KC.MNXT,
        KC.MPRV, KC.MUTE
    ]
]

# Main loop
if __name__ == '__main__':
    if DISPLAY_AVAILABLE:
        oled.fill(0)
        oled.show()

    while True:
        keyboard.go()
        if DISPLAY_AVAILABLE:
            render_wave()
