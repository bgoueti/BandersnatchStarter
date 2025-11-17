import os

from typing import Tuple, Any
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

import pandas as pd
import joblib

class Machine:

    def __init__(self, df: pd.DataFrame):
        '''
        Train a classifier from a DataFrame.
         
        Expects a DataFrame containing at least these columns:
        ['Level', 'Health', 'Energy', 'Sanity', 'Rarity'] or similar.
        Trains a RandomForestClassifier to predict Rarity.
        '''
        if df is None or df.empty:
            raise ValueError("DataFrame is empty - so can't train Machine")
        
        # Copy to avoid mutating caller df 
        data = df.copy()
        
        if 'Rarity' not in data.columns:
            raise ValueError("DataFrame must contain a 'Ra nm m,   vqrity' column for supervised training")
        
        # Features = all columns except Rarity
        self.features = [col for col in data.columns if col != 'Rarity']
        x = data[self.features].astype(float)
        y = data['Rarity'].astype(str)
        
        # Label encode target
        self.labencod = LabelEncoder()
        y_enc = self.labencod.fit_transform(y)
        
        # Keeping a trained model
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        x_train, x_test, y_train, y_test = train_test_split(x, y_enc, test_size=0.2, random_state=42)
        self.model.fit(x_train, y_train)
        
        #Basic training info
        self._train_score = float(accuracy_score(y_test, self.model.predict(x_test)))
        self._classes = list(self.labencod.classes_)

    def __call__(self, feature_basis):
        '''
        Predict label and confidence for the first row of feature_basis.
        Returns (pred_label_string, confidence_float between 0 and 1)
        '''
        if feature_basis is None or feature_basis.empty:
            raise ValueError("feature_basis must be a non-empty DataFrame")
        
        x = feature_basis[self.features].astype(float)
        probs = self.model.predict_proba(x)
        
        # Choose the first sample (main app only passes single-row df)
        best_index = int(probs[0].argmax())
        confidence = float(probs[0][best_index]) 
        pred_label = self.labencod.inverse_transform([best_index])[0]
        return pred_label, confidence

    def save(self, filepath):
        '''
        Save this Machine instance to filepath using joblib.
        '''
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self, filepath)

    @staticmethod
    def open(filepath):
        '''
        Load and return a Machine saved with save().
        '''
        return joblib.load(filepath)

    def info(self):
        '''
        Return siimple information about the trained model.
        '''
        return{
            "classes": self._classes,
            "n_features": len(self.features),
            "features": self.features,
            "validation_accuracy": round(self._train_score, 4)
        }
