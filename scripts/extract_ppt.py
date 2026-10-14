import glob
import os

files = glob.glob('/Users/ansari/Downloads/brand vision new photos/*.ppt')
print('Found PPTs:', len(files))

out_dir = '/tmp/ppt_extracted'
os.makedirs(out_dir, exist_ok=True)

for filepath in files:
    with open(filepath, 'rb') as f:
        data = f.read()
    
    basename = os.path.splitext(os.path.basename(filepath))[0].replace(' ', '_').replace('-', '_')
    img_idx = 0
    
    # Extract JPEGs
    pos = 0
    while True:
        start = data.find(b'\xff\xd8\xff', pos)
        if start == -1:
            break
        end = data.find(b'\xff\xd9', start + 4)
        if end == -1:
            pos = start + 3
            continue
        end += 2
        img_data = data[start:end]
        # Ignore small icons/thumbnails < 20KB
        if len(img_data) > 20000:
            out_path = os.path.join(out_dir, f'{basename}_img{img_idx:02d}.jpg')
            with open(out_path, 'wb') as img_f:
                img_f.write(img_data)
            img_idx += 1
        pos = end
        
    # Extract PNGs
    pos = 0
    while True:
        start = data.find(b'\x89PNG\r\n\x1a\n', pos)
        if start == -1:
            break
        end = data.find(b'IEND', start + 8)
        if end == -1:
            pos = start + 8
            continue
        end += 8
        img_data = data[start:end]
        if len(img_data) > 20000:
            out_path = os.path.join(out_dir, f'{basename}_png{img_idx:02d}.png')
            with open(out_path, 'wb') as img_f:
                img_f.write(img_data)
            img_idx += 1
        pos = end
        
    print(f'{os.path.basename(filepath)}: extracted {img_idx} images')

print('Total extracted in /tmp/ppt_extracted:', len(os.listdir(out_dir)))
