import zlib
import struct
import math
import os

def create_png_with_drawing(width, height, draw_func):
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0)
        for x in range(width):
            r, g, b = draw_func(x / width, y / height)
            raw_data.extend([r, g, b])

    png = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('!IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data)
    png += struct.pack('!I', len(ihdr_data)) + b'IHDR' + ihdr_data + struct.pack('!I', ihdr_crc)

    compressed = zlib.compress(raw_data, level=9)
    idat_crc = zlib.crc32(b'IDAT' + compressed)
    png += struct.pack('!I', len(compressed)) + b'IDAT' + compressed + struct.pack('!I', idat_crc)

    png += struct.pack('!I', 0) + b'IEND' + struct.pack('!I', zlib.crc32(b'IEND'))
    return png

def draw_terminal(nx, ny):
    # Dark Cyber background gradient
    t = (nx + ny) / 2.0
    r = int(15 * (1 - t) + 44 * t)
    g = int(32 * (1 - t) + 83 * t)
    b = int(39 * (1 - t) + 100 * t)

    # Phone Body (Rounded Box)
    if 0.34 <= nx <= 0.66 and 0.22 <= ny <= 0.78:
        # Screen area
        if 0.37 <= nx <= 0.63 and 0.28 <= ny <= 0.72:
            # Credit Card on screen
            if 0.40 <= nx <= 0.60 and 0.42 <= ny <= 0.58:
                return (254, 202, 87) # Gold card
            return (16, 172, 132) # Emerald screen
        return (255, 255, 255) # Phone frame

    # NFC Wireless Waves (Arcs top right)
    cx, cy = 0.72, 0.28
    dist = math.hypot(nx - cx, ny - cy)
    angle = math.atan2(ny - cy, nx - cx)
    if -1.2 <= angle <= 0.2:
        if 0.08 <= dist <= 0.11 or 0.15 <= dist <= 0.18 or 0.22 <= dist <= 0.25:
            return (56, 239, 125) # Neon Green NFC wave

    return (r, g, b)

def draw_cashier(nx, ny):
    # Blue background gradient
    t = (nx + ny) / 2.0
    r = int(30 * (1 - t) + 52 * t)
    g = int(60 * (1 - t) + 172 * t)
    b = int(114 * (1 - t) + 224 * t)

    # Shopping Cart Basket
    if 0.30 <= ny <= 0.60:
        left_limit = 0.28 + (ny - 0.30) * 0.15
        right_limit = 0.72 - (ny - 0.30) * 0.05
        if left_limit <= nx <= right_limit:
            if (nx - left_limit) < 0.04 or (right_limit - nx) < 0.04 or (ny - 0.30) < 0.04 or (0.60 - ny) < 0.04 or (int(nx*50)%4==0) or (int(ny*50)%4==0):
                return (255, 255, 255) # Cart wire
            return (255, 218, 121) # Item filling

    # Cart Handle
    if 0.20 <= nx <= 0.30 and 0.25 <= ny <= 0.38:
        if math.hypot(nx - 0.25, ny - 0.30) <= 0.06:
            return (255, 255, 255)

    # Cart Wheels
    w1 = math.hypot(nx - 0.40, ny - 0.72)
    w2 = math.hypot(nx - 0.65, ny - 0.72)
    if w1 <= 0.07 or w2 <= 0.07:
        if w1 <= 0.03 or w2 <= 0.03:
            return (255, 218, 121)
        return (255, 255, 255)

    return (r, g, b)

def draw_admin(nx, ny):
    # Dark Indigo gradient
    t = (nx + ny) / 2.0
    r = int(44 * (1 - t) + 52 * t)
    g = int(62 * (1 - t) + 152 * t)
    b = int(80 * (1 - t) + 219 * t)

    # Gear wheel
    cx, cy = 0.5, 0.5
    dx, dy = nx - cx, ny - cy
    dist = math.hypot(dx, dy)
    angle = math.atan2(dy, dx)

    # 8 Gear teeth
    tooth = math.sin(angle * 8) > 0
    outer_r = 0.34 if tooth else 0.28

    if 0.12 <= dist <= outer_r:
        if dist <= 0.25 or tooth:
            return (255, 255, 255)

    if 0.08 <= dist < 0.12:
        return (255, 218, 121) # Inner gear core

    return (r, g, b)

if __name__ == "__main__":
    img_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(img_dir, exist_ok=True)

    with open(os.path.join(img_dir, 'favicon.png'), 'wb') as f:
        f.write(create_png_with_drawing(32, 32, draw_cashier))

    with open(os.path.join(img_dir, 'favicon.ico'), 'wb') as f:
        f.write(create_png_with_drawing(32, 32, draw_cashier))

    for size in (192, 512):
        with open(os.path.join(img_dir, f'icon-cashier-{size}.png'), 'wb') as f:
            f.write(create_png_with_drawing(size, size, draw_cashier))
        with open(os.path.join(img_dir, f'icon-terminal-{size}.png'), 'wb') as f:
            f.write(create_png_with_drawing(size, size, draw_terminal))
        with open(os.path.join(img_dir, f'icon-admin-{size}.png'), 'wb') as f:
            f.write(create_png_with_drawing(size, size, draw_admin))

    print("All rich PWA app icons generated successfully!")
