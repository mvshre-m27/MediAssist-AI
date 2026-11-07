import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer

# Numerical features that require standardization
NUMERICAL_FEATURES = [
    'AGE',
    'ANNUALCONTRIBUTION',
    'ANNUALCLAIMAMOUNT',
    'UNITSTOTAL'
]

# Binary / categorical features already encoded as 0 or 1
BINARY_FEATURES = [
    'GENDER_M',
    'SCHEMETYPE_MEDIUM',
    'SCHEMETYPE_PREMIUM',
    'DIAGNOSIS_HYPERTENSION',
    'COVERTYPE_STANDARD',
    'COMORBIDITY_NO_COMORBIDITY',
    'COMPLICATIONDEVELOPMENT_NO_COMPLICATION'
]

ALL_FEATURE_COLUMNS = NUMERICAL_FEATURES + BINARY_FEATURES

def get_preprocessor():
    """
    Build and return a scikit-learn ColumnTransformer
    that standardizes continuous numerical features and passes through binary features.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), NUMERICAL_FEATURES),
            ('bin', 'passthrough', BINARY_FEATURES)
        ],
        remainder='drop'
    )
    return preprocessor

def load_data(filepath='ml/dataset.csv'):
    """
    Load dataset, separate features and target, and map target:
    1 = NON-ADHERENT (Risk class)
    0 = ADHERENT (Baseline class)
    """
    df = pd.read_csv(filepath)
    X = df[ALL_FEATURE_COLUMNS].copy()
    y = (df['ADHERENCE'] == 'NON-ADHERENT').astype(int)
    return X, y
