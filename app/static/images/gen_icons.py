import zlib
import struct
import os

def create_gradient_icon(width, height, color1, color2, badge_color):
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    br, bg, bb = badge_color

    raw_data = bytearray()
    center_x = width / 2
    center_y = height / 2
    badge_radius = width * 0.32

    for y in range(height):
        raw_data.append(0)
        t_y = y / height
        for x in range(width):
            t_x = x / width
            t = (t_x + t_y) / 2.0
            r = int(r1 * (1 - t) + r2 * t)
            g = int(g1 * (1 - t) + g2 * t)
            b = int(b1 * (1 - t) + b2 * t)
            
            dx = x - center_x
            dy = y - center_y
            dist = (dx * dx + dy * dy) ** 0.5
            
            if dist <= badge_radius:
                edge = badge_radius - dist
                if edge < 2:
                    alpha = edge / 2.0
                    r = int(br * alpha + r * (1 - alpha))
                    g = int(bg * alpha + g * (1 - alpha))
                    b = int(bb * alpha + b * (1 - alpha))
                else:
                    r, g, b = br, bg, bb
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

img_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(img_dir, exist_ok=True)

with open(os.path.join(img_dir, 'favicon.png'), 'wb') as f:
    f.write(create_gradient_icon(32, 32, (52, 172, 224), (30, 60, 114), (255, 218, 121)))

with open(os.path.join(img_dir, 'favicon.ico'), 'wb') as f:
    f.write(create_gradient_icon(32, 32, (52, 172, 224), (30, 60, 114), (255, 218, 121)))

# 1. Cashier Icons (Sky Blue + Bright Gold)
for size in (192, 512):
    with open(os.path.join(img_dir, f'icon-cashier-{size}.png'), 'wb') as f:
        f.write(create_gradient_icon(size, size, (52, 172, 224), (30, 60, 114), (255, 218, 121)))

# 2. Terminal Icons (Dark Cyber + Neon Green)
for size in (192, 512):
    with open(os.path.join(img_dir, f'icon-terminal-{size}.png'), 'wb') as f:
        f.write(create_gradient_icon(size, size, (15, 32, 39), (44, 83, 100), (56, 239, 125)))

# 3. Admin Icons (Royal Blue + Coral Red)
for size in (192, 512):
    with open(os.path.join(img_dir, f'icon-admin-{size}.png'), 'wb') as f:
        f.write(create_gradient_icon(size, size, (56, 103, 214), (43, 85, 183), (255, 118, 117)))

print("All dedicated PWA app icons generated successfully!")
