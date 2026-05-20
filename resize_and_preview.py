import os
from PIL import Image

def resize_images(src_dir, dest_dir, target_width=1000):
    os.makedirs(dest_dir, exist_ok=True)
    files = sorted([f for f in os.listdir(src_dir) if f.endswith('.png')])
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
            else:
                img.save(dest_path)
                print(f"Copied {filename} (already small): {w}x{h}")

def create_preview_html(image_dir, html_path):
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
        html_content += f"""
    <div class="page-container">
        <h3>Page {f.split('_')[-1].split('.')[0]}</h3>
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

if __name__ == '__main__':
    src = "/Users/kenyim/.gemini/antigravity/scratch/math-answer-review/raw_pages"
    dest = "/Users/kenyim/.gemini/antigravity/scratch/math-answer-review/resized"
    resize_images(src, dest)
    create_preview_html(dest, "/Users/kenyim/.gemini/antigravity/scratch/math-answer-review/preview.html")
