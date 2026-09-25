import os
from ml_module import classify_file
def extract_features(filepath):
    size = os.path.getsize(filepath)
    ext = os.path.splitext(filepath)[1].lower()
    return {
        'size': size,
        'extension': ext
    }

def classify_file(filepath):
    features = extract_features(filepath)
    # Dummy rule-based for now
    if features['size'] > 50 * 1024 * 1024:  # > 50 MB
        return 'suspicious'
    if features['extension'] in ['.exe', '.bat', '.sh']:
        return 'suspicious'
    return 'safe'
# inside upload()
temp_path = os.path.join('uploads', file.filename)
file.save(temp_path)
result = classify_file(temp_path)
if result == 'suspicious':
    flash('Warning: File may be suspicious!')
    # Optionally ask user to confirm before continuing