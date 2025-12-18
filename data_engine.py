import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

class HybridDataEngine:
    def __init__(self, enron_path, phishing_path):
        self.enron_path = enron_path
        self.phishing_path = phishing_path
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        # Map clean names to actual CSV column names
        self.url_feature_map = {
            'having_IPhaving_IP_Address': 'having_IP_Address',
            'URLURL_Length': 'URL_Length',
            'having_At_Symbol': 'having_At_Symbol',
            'double_slash_redirecting': 'double_slash_redirecting',
            'Prefix_Suffix': 'Prefix_Suffix',
            'having_Sub_Domain': 'having_Sub_Domain'
        }
        self.url_features = list(self.url_feature_map.values())
        
    def load_and_process_enron(self):
        print("Loading Enron Spam Data...")
        try:
            df = pd.read_csv(self.enron_path, encoding='latin-1') # Common encoding for this dataset
        except UnicodeDecodeError:
            df = pd.read_csv(self.enron_path)
            
        # Combine Subject and Message, handle NaNs
        df['text'] = df['Subject'].fillna('').astype(str) + " " + df['Message'].fillna('').astype(str)
        
        # Label Encoding: spam=1, ham=0
        df['label'] = df['Spam/Ham'].map({'spam': 1, 'ham': 0})
        
        # TF-IDF
        print("Vectorizing Enron Data...")
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(df['text'])
        
        # Create DataFrame for features (toarray() converts sparse matrix to dense array)
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=self.tfidf_vectorizer.get_feature_names_out())
        
        # Add URL features columns (set to 0 for email data)
        for feat in self.url_features:
            tfidf_df[feat] = 0
            
        tfidf_df['label'] = df['label']
        
        return tfidf_df

    def load_and_process_phishing(self):
        print("Loading Phishing Website Data...")
        df = pd.read_csv(self.phishing_path)
        
        # Select features using the map keys (actual columns)
        actual_cols = list(self.url_feature_map.keys())
        features_df = df[actual_cols].copy()
        
        # Rename to clean names
        features_df = features_df.rename(columns=self.url_feature_map)
        
        # Label Encoding: -1 (Phishing) -> 1, 1 (Legit) -> 0
        # Note: In UCI dataset, -1 is usually phishing.
        features_df['label'] = df['Result'].apply(lambda x: 1 if x == -1 else 0)
        
        # Add TF-IDF columns (set to 0 for URL data)
        tfidf_cols = self.tfidf_vectorizer.get_feature_names_out()
        
        # Create a DataFrame with 0s for TF-IDF features
        # We use a dictionary to create the dataframe efficiently
        zeros_data = np.zeros((len(features_df), len(tfidf_cols)))
        tfidf_part = pd.DataFrame(zeros_data, columns=tfidf_cols)
        
        # Concatenate
        final_df = pd.concat([tfidf_part, features_df.reset_index(drop=True)], axis=1)
        
        return final_df

    def build_hybrid_dataset(self):
        # Process Enron (fits vectorizer)
        enron_df = self.load_and_process_enron()
        
        # Process Phishing (uses fitted vectorizer features as placeholders)
        phishing_df = self.load_and_process_phishing()
        
        print("Merging Datasets...")
        hybrid_df = pd.concat([enron_df, phishing_df], axis=0, ignore_index=True)
        
        # Fill NaNs if any (shouldn't be, but safe practice)
        hybrid_df = hybrid_df.fillna(0)
        
        print(f"Hybrid Dataset Shape: {hybrid_df.shape}")
        return hybrid_df

    def save_vectorizer(self, path='tfidf_vectorizer.pkl'):
        joblib.dump(self.tfidf_vectorizer, path)

if __name__ == "__main__":
    engine = HybridDataEngine(
        'enron_spam_dataset/enron_spam_data.csv',
        'phishing_website_dataset/phishing_website_dataset.csv'
    )
    df = engine.build_hybrid_dataset()
    engine.save_vectorizer()
    
    # Save processed data
    print("Saving processed data...")
    df.to_pickle('hybrid_data.pkl')
    print("Done.")
