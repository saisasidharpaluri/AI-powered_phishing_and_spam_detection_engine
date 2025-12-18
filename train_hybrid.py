import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import time

def train_models():
    print("Loading Hybrid Data...")
    df = pd.read_pickle('hybrid_data.pkl')
    
    X = df.drop('label', axis=1)
    y = df['label']
    
    print(f"Data Shape: {X.shape}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'SVM': SVC(kernel='linear', probability=True, random_state=42) 
        # Note: probability=True is needed for predict_proba, but slows down SVC. 
        # If too slow, we might switch to LinearSVC with CalibratedClassifierCV.
    }
    
    best_model = None
    best_accuracy = 0
    best_model_name = ""
    
    results = {}
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        start_time = time.time()
        model.fit(X_train, y_train)
        train_time = time.time() - start_time
        print(f"Training time: {train_time:.2f}s")
        
        print(f"Evaluating {name}...")
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Accuracy: {accuracy:.4f}")
        print(classification_report(y_test, y_pred))
        
        results[name] = accuracy
        
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = model
            best_model_name = name
            
    print(f"\nBest Model: {best_model_name} with Accuracy: {best_accuracy:.4f}")
    
    # Save best model
    print(f"Saving {best_model_name} to hybrid_security_model.pkl...")
    joblib.dump(best_model, 'hybrid_security_model.pkl')
    print("Model saved.")

if __name__ == "__main__":
    train_models()
