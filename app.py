from flask import Flask, request, send_file, render_template_string
import os, zipfile, requests

app = Flask(__name__)

HTML_FORM = """
<!doctype html>
<html>
<head><title>Script to Zip</title></head>
<body>
    <h1>Script to Images → ZIP</h1>
    <form method="post">
        <textarea name="script" rows="10" cols="60" placeholder="Paste your script here..."></textarea><br><br>
        <button type="submit">Generate ZIP</button>
    </form>
</body>
</html>
"""

def generate_images_from_script(script, output_zip="video_project.zip"):
    os.makedirs("output_images", exist_ok=True)
    for f in os.listdir("output_images"):
        os.remove(os.path.join("output_images", f))

    lines = [line.strip() for line in script.split("\n") if line.strip()]
    image_files = []

    for i, line in enumerate(lines, start=1):
        url = f"https://image.pollinations.ai/prompt/{line.replace(' ', '%20')}"
        image_path = f"output_images/scene_{i}.png"
        r = requests.get(url)
        if r.status_code == 200:
            with open(image_path, "wb") as f:
                f.write(r.content)
            image_files.append(image_path)

    script_file = "output_images/script.txt"
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(script)

    with zipfile.ZipFile(output_zip, "w") as zipf:
        for file in image_files + [script_file]:
            zipf.write(file)

    return output_zip

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        script = request.form["script"]
        zip_path = generate_images_from_script(script)
        return send_file(zip_path, as_attachment=True)
    return render_template_string(HTML_FORM)

if __name__ == "__main__":
    # important for Render/Heroku
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
