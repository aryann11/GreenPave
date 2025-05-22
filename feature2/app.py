from flask import Blueprint, render_template, request, jsonify
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import joblib
import os

feature2_bp = Blueprint('feature2', __name__,
                       template_folder='templates',
                       static_folder='static')

# Create directories if they don't exist
os.makedirs('recomm/models', exist_ok=True)

def load_and_preprocess_data():
    try:
        df = pd.read_csv('C:/GEN AI/GreenPave/feature2/Crop_recommendation.csv')
    except FileNotFoundError:
        raise FileNotFoundError("Crop_recommendation.csv file not found. Please ensure the file is in the root directory.")
    
    X = df.drop('label', axis=1)
    y = df['label']
    
    le = LabelEncoder()
    y = le.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    return X_train, X_test, y_train, y_test, le, X.columns

def train_model():
    X_train, X_test, y_train, y_test, le, feature_names = load_and_preprocess_data()
    
    model = xgb.XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
    
    cv_scores = cross_val_score(model, X_train, y_train, cv=5)
    print(f"\nCross-validation scores: {cv_scores}")
    print(f"Average CV score: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    print("\nModel Evaluation Metrics:")
    print(f"Accuracy: {accuracy:.3f}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall: {recall:.3f}")
    print(f"F1 Score: {f1:.3f}")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    model_path = os.path.join('recomm', 'models', 'crop_model.joblib')
    le_path = os.path.join('recomm', 'models', 'label_encoder.joblib')
    
    joblib.dump(model, model_path)
    joblib.dump(le, le_path)
    
    return model, le, feature_names

def get_model():
    model_path = os.path.join('recomm', 'models', 'crop_model.joblib')
    le_path = os.path.join('recomm', 'models', 'label_encoder.joblib')
    
    if os.path.exists(model_path) and os.path.exists(le_path):
        try:
            model = joblib.load(model_path)
            le = joblib.load(le_path)
            _, _, _, _, _, feature_names = load_and_preprocess_data()
            return model, le, feature_names
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Training new model...")
            return train_model()
    else:
        print("Model files not found. Training new model...")
        return train_model()

@feature2_bp.route('/')
def home():
    return render_template('features/feature2/index.html')

@feature2_bp.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        features = np.array([[
            float(data['N']),
            float(data['P']),
            float(data['K']),
            float(data['temperature']),
            float(data['humidity']),
            float(data['ph']),
            float(data['rainfall'])
        ]])
        
        model, le, _ = get_model()
        prediction = model.predict(features)
        crop = le.inverse_transform(prediction)[0]
        
        return jsonify({'prediction': crop})
    except Exception as e:
        return jsonify({'error': str(e)}), 400