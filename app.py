from flask import Flask, render_template, request, redirect, flash, send_from_directory, url_for
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet, InvalidToken
import os

UPLOAD_FOLDER = 'uploads'
KEY_FILE = 'Secret.key'

app = Flask(__name__)
app.secret_key = 'supsersecretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Generate and load key functions
def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)

def load_key():
    return open(KEY_FILE, "rb").read()

# Encryption
def encrypt(file_path, key):
    f = Fernet(key)
    with open(file_path, "rb") as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    encrypted_path = file_path + ".enc"
    with open(encrypted_path, "wb") as file:
        file.write(encrypted_data)
    return os.path.basename(encrypted_path)

# Decryption
def decrypt(file_path, key):
    f = Fernet(key)
    with open(file_path, "rb") as file:
        encrypted_data = file.read()
    try:
        decrypted_data = f.decrypt(encrypted_data)
    except InvalidToken:
        return None
    decrypted_path = file_path.replace(".enc", "")
    with open(decrypted_path, "wb") as file:
        file.write(decrypted_data)
    return os.path.basename(decrypted_path)

# Index Route
@app.route("/", methods=["GET", "POST"])
def index():
    download_link = None
    if request.method == "POST":
        action = request.form.get("action")
        uploaded_file = request.files.get("file")

        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)

            if action == "encrypt":
                generate_key()
                key = load_key()
                new_filename = encrypt(file_path, key)
                flash("File encrypted successfully!", "success")
                download_link = url_for('download_file', filename=new_filename)

            elif action == "decrypt":
                if not os.path.exists(KEY_FILE):
                    flash("Key not found for decryption.", "danger")
                else:
                    key = load_key()
                    result = decrypt(file_path, key)
                    if result:
                        flash("File decrypted successfully!", "success")
                        download_link = url_for('download_file', filename=result)
                    else:
                        flash("Invalid key or file. Decryption failed.", "danger")

        else:
            flash("No file selected.", "warning")

    return render_template("index.html", download_link=download_link)

# Download Route
@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)


# set FLASK_APP=app.py
# set FLASK_ENV=development
# python -m flask run
