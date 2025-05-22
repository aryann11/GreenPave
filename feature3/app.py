from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import numpy as np

feature3_bp = Blueprint('feature3', __name__,
                       template_folder='templates',
                       static_folder='static')

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join('static', 'uploads')  # Relative to application root

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load model
try:
    model = load_model('C:/GEN AI/GreenPave/feature3/mango_disease_mobilenet_model.h5')
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

class_mapping = {
    0: 'Anthracnose',
    1: 'Bacterial Canker',
    2: 'Cutting Weevil',
    3: 'Die Back',
    4: 'Gall Midge',
    5: 'Healthy',
    6: 'Powdery Mildew',
    7: 'Sooty Mould'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    return preprocess_input(img_array)

@feature3_bp.route('/')
def index():
    return render_template('features/feature3/index.html')

@feature3_bp.route('/predict', methods=['POST'])
def mango_predict():
    if 'image' not in request.files:
        flash('No file part')
        return redirect(url_for('feature3.index'))
    
    file = request.files['image']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('feature3.index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Fix relative path for template usage (relative to /static)
        rel_filepath = os.path.join('uploads', filename)

        try:
            img = preprocess_image(filepath)
            predictions = model.predict(img)[0]
            predicted_index = np.argmax(predictions)
            predicted_class = class_mapping[predicted_index]
            confidence = float(predictions[predicted_index])
            result_probs = dict(zip(class_mapping.values(), map(float, predictions)))

            return render_template('features/feature3/result.html',
                                image_url=rel_filepath,
                                disease=predicted_class,
                                confidence=round(confidence * 100, 2),
                                probabilities=result_probs)
        except Exception as e:
            return render_template('features/feature3/result.html', error=str(e))
    
    flash('Allowed file types are png, jpg, jpeg, gif')
    return redirect(url_for('feature3.index'))
