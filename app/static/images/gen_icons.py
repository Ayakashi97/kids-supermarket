import zlib
import struct
import os

def create_png(width, height, color_rgb):
    r, g, b = color_rgb
    png = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('!IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data)
    png += struct.pack('!I', len(ihdr_data)) + b'IHDR' + ihdr_data + struct.pack('!I', ihdr_crc)
    
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0)
        for x in range(width):
            raw_data.extend([r, g, b])
            
    compressed = zlib.compress(raw_data)
    idat_crc = zlib.crc32(b'IDAT' + compressed)
    png += struct.pack('!I', len(compressed)) + b'IDAT' + compressed + struct.pack('!I', idat_crc)
    
    png += struct.pack('!I', 0) + b'IEND' + struct.pack('!I', zlib.crc32(b'IEND'))
    return png

os.makedirs('/Users/jan/projects/supermarket/app/static/images', exist_ok=True)
with open('/Users/jan/projects/supermarket/app/static/images/favicon.png', 'wb') as f:
    f.write(create_png(32, 32, (52, 172, 224)))

with open('/Users/jan/projects/supermarket/app/static/images/favicon.ico', 'wb') as f:
    f.write(create_png(32, 32, (52, 172, 224)))

with open('/Users/jan/projects/supermarket/app/static/images/icon-192.png', 'wb') as f:
    f.write(create_png(192, 192, (30, 60, 114)))

with open('/Users/jan/projects/supermarket/app/static/images/icon-512.png', 'wb') as f:
    f.write(create_png(512, 512, (30, 60, 114)))

print("Favicons generated successfully!")
