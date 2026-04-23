import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn.cluster import KMeans
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, classification_report, confusion_matrix
)
import warnings
warnings.filterwarnings('ignore')

FEATURES = ['attendance', 'internal_marks', 'assignment_score',
            'quiz_score', 'lab_marks', 'study_hours']
TARGET_REG = 'semester_marks'
TARGET_CLF = 'grade_label'
GRADE_ORDER = ['A', 'B', 'C', 'D', 'F']


# Regression

def train_regression_models(df: pd.DataFrame):
    X = df[FEATURES]
    y = df[TARGET_REG]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    models = {
        'Linear Regression':    LinearRegression(),
        'Random Forest':        RandomForestRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting':    GradientBoostingRegressor(n_estimators=100, random_state=42),
    }

    results = {}
    trained  = {}

    for name, model in models.items():
        X_tr = X_train_s if name == 'Linear Regression' else X_train
        X_te = X_test_s  if name == 'Linear Regression' else X_test
        model.fit(X_tr, y_train)
        preds = model.predict(X_te)
        results[name] = {
            'RMSE':  round(np.sqrt(mean_squared_error(y_test, preds)), 3),
            'MAE':   round(mean_absolute_error(y_test, preds), 3),
            'R2':    round(r2_score(y_test, preds), 4),
        }
        trained[name] = model

    best_name = max(results, key=lambda k: results[k]['R2'])

    # Feature importance from best tree-based model
    best_tree = trained.get('Random Forest') or trained.get('Gradient Boosting')
    feat_imp  = dict(zip(FEATURES, best_tree.feature_importances_.round(4)))

    return {
        'results':        results,
        'best_model':     best_name,
        'best_r2':        results[best_name]['R2'],
        'feature_importance': feat_imp,
        'trained_models': trained,
        'scaler':         scaler,
        'X_test':         X_test,
        'y_test':         y_test,
    }


def predict_marks(model, scaler, X: pd.DataFrame, is_linear: bool = False) -> np.ndarray:
    if is_linear:
        return model.predict(scaler.transform(X))
    return model.predict(X)


# Classification

def train_classification_models(df: pd.DataFrame):
    X = df[FEATURES]
    le = LabelEncoder()
    le.fit(GRADE_ORDER)
    y = le.transform(df[TARGET_CLF])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,
                                                         random_state=42, stratify=y)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    models = {
        'Logistic Regression':  LogisticRegression(max_iter=1000, random_state=42),
        'Decision Tree':        DecisionTreeClassifier(max_depth=6, random_state=42),
        'Random Forest':        RandomForestClassifier(n_estimators=100, random_state=42),
    }

    results  = {}
    trained  = {}

    for name, model in models.items():
        X_tr = X_train_s if name == 'Logistic Regression' else X_train
        X_te = X_test_s  if name == 'Logistic Regression' else X_test
        model.fit(X_tr, y_train)
        preds = model.predict(X_te)
        results[name] = {
            'Accuracy':  round(accuracy_score(y_test, preds), 4),
            'Report':    classification_report(y_test, preds,
                             labels=range(len(le.classes_)),
                             target_names=le.classes_, output_dict=True, zero_division=0),
            'Confusion': confusion_matrix(y_test, preds).tolist(),
        }
        trained[name] = model

    best_name = max(results, key=lambda k: results[k]['Accuracy'])

    rf = trained['Random Forest']
    feat_imp = dict(zip(FEATURES, rf.feature_importances_.round(4)))

    return {
        'results':            results,
        'best_model':         best_name,
        'best_accuracy':      results[best_name]['Accuracy'],
        'feature_importance': feat_imp,
        'trained_models':     trained,
        'label_encoder':      le,
        'scaler':             scaler,
        'X_test':             X_test,
        'y_test':             y_test,
        'grade_classes':      list(le.classes_),
    }


# Clustering

CLUSTER_PERSONAS = {
    0: {'name': 'High Achievers',       'color': '#27AE60'},
    1: {'name': 'Average Performers',   'color': '#F39C12'},
    2: {'name': 'At-Risk Students',     'color': '#E74C3C'},
    3: {'name': 'Inconsistent Learners','color': '#9B59B6'},
}

def train_clustering(df: pd.DataFrame, k: int = None):
    cluster_features = ['attendance', 'internal_marks', 'semester_marks',
                        'study_hours', 'assignment_score']
    X = df[cluster_features]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Elbow method
    inertias = []
    k_range  = range(2, 8)
    for ki in k_range:
        km = KMeans(n_clusters=ki, random_state=42, n_init=10)
        km.fit(X_scaled)
        inertias.append(km.inertia_)

    # Pick optimal k if not specified
    if k is None:
        diffs = np.diff(inertias)
        diffs2 = np.diff(diffs)
        k = int(k_range[np.argmax(diffs2) + 1]) if len(diffs2) > 0 else 3
        k = max(3, min(k, 4))

    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)

    df_out = df.copy()
    df_out['cluster_id'] = labels

    # Auto-label clusters by avg semester_marks rank
    cluster_means = df_out.groupby('cluster_id')['semester_marks'].mean().sort_values(ascending=False)
    persona_map   = {}
    persona_keys  = list(CLUSTER_PERSONAS.keys())
    for rank, cid in enumerate(cluster_means.index):
        p = CLUSTER_PERSONAS.get(rank, {'name': f'Group {rank}', 'color': '#95A5A6'})
        persona_map[cid] = p['name']

    df_out['cluster_name'] = df_out['cluster_id'].map(persona_map)

    cluster_profiles = (
        df_out.groupby('cluster_name')[cluster_features + ['semester_marks']]
        .mean()
        .round(2)
        .reset_index()
    )

    return {
        'df':              df_out,
        'model':           km,
        'k':               k,
        'inertias':        list(zip(k_range, inertias)),
        'cluster_profiles': cluster_profiles,
        'cluster_sizes':   df_out['cluster_name'].value_counts().to_dict(),
        'persona_map':     persona_map,
        'features_used':   cluster_features,
        'X_scaled':        X_scaled,
    }
