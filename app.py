from flask import Flask, request, send_file, render_template_string, abort
except Exception as e:
err_path = os.path.join(tmpdir, f"scene_{i:03d}_exception.txt")
with open(err_path, 'w', encoding='utf-8') as ef:
ef.write(f"Exception while fetching prompt: {safe_line}\n{repr(e)}")
image_paths.append(err_path)


return image_paths




@app.route('/', methods=['GET'])
def index():
return render_template_string(HTML_FORM)




@app.route('/generate', methods=['POST'])
def generate():
script = request.form.get('script', '')
if not script.strip():
abort(400, 'No script provided')


try:
max_lines = int(request.form.get('max_lines', 20))
except Exception:
max_lines = 20
max_lines = max(1, min(50, max_lines))


# split lines and keep only non-empty
lines = [ln.strip() for ln in script.split('\n') if ln.strip()]
lines = lines[:max_lines]


# Use a temp directory per request to avoid collisions
workdir = tempfile.mkdtemp(prefix='script_to_zip_')
try:
# save script file
script_file = os.path.join(workdir, 'script.txt')
with open(script_file, 'w', encoding='utf-8') as sf:
sf.write(script)


# generate images
image_files = generate_images_lines(lines, workdir)


# create zip file
zip_name = f"video_project_{uuid.uuid4().hex[:8]}.zip"
zip_path = os.path.join(workdir, zip_name)
with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
# add images and script with nicer names
for p in sorted(image_files):
arcname = os.path.basename(p)
zf.write(p, arcname)
zf.write(script_file, 'script.txt')


# send file
return send_file(zip_path, as_attachment=True, download_name=zip_name)


finally:
# cleanup: remove the temp directory after request finishes sending
# Note: send_file reads file before returning, so it's safe to cleanup here.
shutil.rmtree(workdir, ignore_errors=True)




if __name__ == '__main__':
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
