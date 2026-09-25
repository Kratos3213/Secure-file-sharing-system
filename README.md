# Secure File Sharing

A Flask application for uploading, encrypting, storing, and downloading files securely. Files are encrypted with Fernet before they are stored. Google Drive can be used as the encrypted file storage provider.

## Features

- User registration and login
- Password hashing with Werkzeug
- Fernet encryption before storage
- Google Drive storage for encrypted files
- Decryption only when an authorized user downloads a file
- File sharing between registered users
- Bootstrap-based responsive interface
- Windows executable build with a custom app icon

## Run From Source

Open PowerShell in the project folder:

```powershell
cd "C:\Users\vivek\Desktop\SECURE FILE SHARING\secure-file-sharing"
python -m pip install -r requirements.txt
python app.py
```

Open the application at:

```text
http://127.0.0.1:5000
```

## Google Drive Setup

Google Drive storage requires an OAuth Desktop application credential.

1. Open the Google Cloud Console.
2. Create or select a project.
3. Enable the **Google Drive API**.
4. Configure the OAuth consent screen as **External**.
5. Add your Google account under **Test users** while the app is in Testing mode.
6. Create an OAuth client ID with application type **Desktop app**.
7. Download the JSON file and rename it to `credentials.json`.
8. Place it in the project folder beside `app.py`.

On the first upload, a browser window opens for Google authorization. After approval, the app creates `token.json` automatically.

Never publish or share `credentials.json` or `token.json`.

## Storage Behavior

The upload flow is:

1. The user selects a file.
2. The app reads the file and encrypts it with Fernet.
3. Only the encrypted bytes are uploaded to Google Drive.
4. The database stores the Google Drive file ID and encryption key.
5. On download, the encrypted bytes are fetched and decrypted in memory.
6. The original file is sent to the authorized user's browser.

The database is stored in `instance/database.db`.

## Windows Executable

The packaged application is located at:

```text
dist\SecureFileSharing\SecureFileSharing.exe
```

Start it with:

```powershell
cd "dist\SecureFileSharing"
.\SecureFileSharing.exe
```

Then open:

```text
http://127.0.0.1:5000
```

The executable package must contain:

- `SecureFileSharing.exe`
- `credentials.json`
- `instance\database.db`
- The `_internal` folder created by PyInstaller

The downloadable package is `SecureFileSharing.zip` in the project folder. Extract the complete ZIP before running the executable.

## Rebuild the Executable

The project includes `app_icon.ico` for the Windows application icon.

```powershell
pyinstaller --noconfirm --clean --onedir `
  --name SecureFileSharing `
  --icon app_icon.ico `
  --add-data "templates;templates" `
  --add-data "static;static" `
  app.py
```

Copy `credentials.json` and the desired `instance\database.db` into `dist\SecureFileSharing` after rebuilding.

## Project Structure

```text
secure-file-sharing/
├── app.py
├── models.py
├── crypto_utils.py
├── drive_storage.py
├── ml_module.py
├── requirements.txt
├── README.md
├── app_icon.ico
├── static/
│   ├── css/
│   └── js/
├── templates/
├── instance/
│   └── database.db
└── uploads/
    └── encrypted/
```

## Security Notes

- Use a strong production `SECRET_KEY` instead of the development default.
- Keep OAuth credentials, tokens, and the database private.
- Do not commit `credentials.json`, `token.json`, or private databases.
- Run behind a production WSGI server before exposing the application beyond your local computer.
- Google Drive must be available for encrypted uploads and downloads when cloud storage is enabled.
