import os
from PIL import Image
from config import RAW_PAGES_DIR, RESIZED_DIR, PREVIEW_PATH

def resize_images(src_dir=RAW_PAGES_DIR, dest_dir=RESIZED_DIR, target_width=1000):
    """Resize raw page images to standard width for cropping consistency."""
    os.makedirs(dest_dir, exist_ok=True)
    files = sorted([f for f in os.listdir(src_dir) if f.endswith('.png')])
    
    resized_count = 0
    for filename in files:
        src_path = os.path.join(src_dir, filename)
        dest_path = os.path.join(dest_dir, filename)
        with Image.open(src_path) as img:
            w, h = img.size
            if w > target_width:
                ratio = target_width / float(w)
                new_h = int(float(h) * ratio)
                resized_img = img.resize((target_width, new_h), Image.Resampling.LANCZOS)
                resized_img.save(dest_path, optimize=True)
                print(f"Resized {filename}: {w}x{h} -> {target_width}x{new_h}")
                resized_count += 1
            else:
                img.save(dest_path)
                print(f"Copied {filename} (already small): {w}x{h}")
                
    return resized_count

def create_preview_html(image_dir=RESIZED_DIR, html_path=PREVIEW_PATH):
    """Generate preview HTML showing all resized PDF pages."""
    files = sorted([f for f in os.listdir(image_dir) if f.endswith('.png')])
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>PDF Page Preview</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #1e1e1e;
            color: #ccc;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }
        .page-container {
            margin-bottom: 40px;
            background: #2a2a2a;
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
            text-align: center;
        }
        .page-container h3 {
            margin-top: 0;
            color: #fff;
        }
        img {
            max-width: 100%;
            height: auto;
            border: 1px solid #444;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <h1>PDF Scanned Page Previews</h1>
"""
    for f in files:
        # Resolve page numbering safely without hardcoding
        try:
            page_lbl = f.split('_')[-1].split('.')[0]
        except Exception:
            page_lbl = f
            
        html_content += f"""
    <div class="page-container">
        <h3>Page {page_lbl}</h3>
        <img src="resized/{f}" alt="Page {f}">
    </div>
"""
    html_content += """
</body>
</html>
"""
    with open(html_path, 'w') as out_f:
        out_f.write(html_content)
    print("Preview HTML generated at:", html_path)
    return len(files)

if __name__ == '__main__':
    resize_images()
    create_preview_html()
