from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__)

# Load the trained model and vectorizer
model = None
vectorizer = None

def load_model():
    global model, vectorizer
    try:
        model = joblib.load('hybrid_security_model.pkl')
        vectorizer = joblib.load('tfidf_vectorizer.pkl')
        print("Model and vectorizer loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")

def extract_url_features(url):
    """Extract features from a URL"""
    features = {}
    
    # having_IP_Address: Check if URL contains IP address
    features['having_IP_Address'] = 1 if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url) else -1
    
    # URL_Length: 1 if short (<54), 0 if medium (54-75), -1 if long (>75)
    url_len = len(url)
    if url_len < 54:
        features['URL_Length'] = 1
    elif url_len <= 75:
        features['URL_Length'] = 0
    else:
        features['URL_Length'] = -1
    
    # having_At_Symbol: -1 if '@' present, 1 otherwise
    features['having_At_Symbol'] = -1 if '@' in url else 1
    
    # double_slash_redirecting: -1 if '//' appears after position 7, 1 otherwise
    features['double_slash_redirecting'] = -1 if url.find('//', 7) != -1 else 1
    
    # Prefix_Suffix: -1 if '-' in domain, 1 otherwise
    features['Prefix_Suffix'] = -1 if '-' in url.split('/')[0] else 1
    
    # having_Sub_Domain: Count dots in domain
    domain = url.split('/')[0]
    dot_count = domain.count('.')
    if dot_count == 1:
        features['having_Sub_Domain'] = 1
    elif dot_count == 2:
        features['having_Sub_Domain'] = 0
    else:
        features['having_Sub_Domain'] = -1
    
    return features

def analyze_input(input_text, input_type):
    """Analyze email text or URL and return threat score"""
    try:
        # Check if model and vectorizer are loaded
        if model is None or vectorizer is None:
            return {
                'error': 'Model not loaded. Please train the model first.',
                'security_score': 0,
                'threat_level': 'Unknown',
            'is_malicious': bool(False)
            # Use TF-IDF for email text
            tfidf_features = vectorizer.transform([input_text]).toarray()[0]
            
            # Add URL features as zeros for email
            url_features = [0] * 6  # 6 URL features
            
            # Combine features in correct order (TF-IDF first, then URL features)
            features = list(tfidf_features) + url_features
            
        else:  # URL
            # TF-IDF features as zeros for URL
            tfidf_features = [0] * len(vectorizer.get_feature_names_out())
            
            # Extract URL features
            url_feat_dict = extract_url_features(input_text)
            url_features = [
                url_feat_dict['having_IP_Address'],
                url_feat_dict['URL_Length'],
                url_feat_dict['having_At_Symbol'],
                url_feat_dict['double_slash_redirecting'],
                url_feat_dict['Prefix_Suffix'],
                url_feat_dict['having_Sub_Domain']
            ]
            
            # Combine features
            features = tfidf_features + url_features
        
        # Convert to DataFrame
        feature_df = pd.DataFrame([features])
        
        # Get prediction probability
        proba = model.predict_proba(feature_df)[0]
        
        # Threat probability (class 1 = malicious)
        threat_score = proba[1] * 100
        
        return {
            'security_score': round(100 - threat_score, 2),  # Safety score (inverse of threat)
            'threat_level': get_threat_level(threat_score),
            'is_malicious': bool(threat_score > 50)
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'security_score': 0,
            'threat_level': 'Unknown',
            'is_malicious': False
        }

def get_threat_level(threat_score):
    """Convert threat score bool(False)tegorical level"""
    if threat_score < 20:
        return 'Very Low'
    elif threat_score < 40:
        return 'Low'
    elif threat_score < 60:
        return 'Medium'
    elif threat_score < 80:
        return 'High'
    else:
        return 'Critical'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    input_text = data.get('input_text', '')
    input_type = data.get('input_type', 'email')
    
    if not input_text:
        return jsonify({'error': 'No input provided'}), 400
    
    result = analyze_input(input_text, input_type)
    return jsonify(result)

if __name__ == '__main__':
    load_model()
    app.run(debug=True, port=5000)
