from flask import Flask, request, render_template, send_file
import os
import io
from dotenv import load_dotenv
from utils import encrypt_file, decrypt_file

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

load_dotenv()
key = os.getenv("AES_KEY")
if not key or len(key) != 32:
    raise ValueError(f"AES_KEY must be exactly 32 characters. Current length: {len(key) if key else 'None'}")
key = key.encode()



@app.route('/')
def index():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    data = file.read()
    nonce, tag, ciphertext = encrypt_file(data, key)
    with open(f"{'uploads'}/{file.filename}.enc", 'wb') as f:
        f.write(nonce + tag + ciphertext)
    return 'File uploaded and encrypted successfully!'

@app.route('/download/<filename>')
def download(filename):
    with open(f"{UPLOAD_FOLDER}/{filename}", 'rb') as f:
        content = f.read()
        nonce = content[:16]
        tag = content[16:32]
        ciphertext = content[32:]
        decrypted = decrypt_file(nonce, tag, ciphertext, key)
    return send_file(
        io.BytesIO(decrypted),
        download_name=filename.replace('.enc', ''),
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(debug=True)

