import os
import sys
import time
import numpy as np

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_PATH   = os.path.join(BASE_DIR, 'data', 'student_data_500.csv')
CHART_DIR   = os.path.join(BASE_DIR, 'outputs', 'charts')
OUTPUT_DIR  = os.path.join(BASE_DIR, 'outputs')

sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

from data_pro import run_pipeline, get_at_risk_students, get_summary_stats
from ml_models import train_regression_models, train_classification_models, train_clustering
from visual import (
    plot_distributions, plot_correlation_heatmap, plot_grade_distribution,
    plot_risk_distribution, plot_attendance_vs_marks, plot_study_hours_vs_marks,
    plot_boxplots_by_grade, plot_feature_importance, plot_regression_results,
    plot_confusion_matrix, plot_model_comparison, plot_clusters, plot_kpi_summary
)
from exel_repo import generate_excel_report
from pdf_report import generate_pdf_report

os.makedirs(CHART_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def log(msg, symbol='✓'):
    print(f'  {symbol}  {msg}')


def run():
    print('\n' + '='*60)
    print('  AI-POWERED SMART CAMPUS ANALYTICS SYSTEM')
    print('  Early Risk Detection Pipeline v1.0')
    print('='*60 + '\n')
    t0 = time.time()

    # ── 1. Data Processing ──────────────────────────────────────────
    print('[ Phase 1 ] Data Processing & Feature Engineering')
    df = run_pipeline(DATA_PATH)
    stats = get_summary_stats(df)
    at_risk = get_at_risk_students(df)
    log(f'Loaded {len(df)} students, {df.shape[1]} features')
    log(f'Feature engineering complete — risk scores, grades, tiers assigned')
    log(f'At-risk students identified: {stats["at_risk_count"]} ({stats["at_risk_count"]/len(df)*100:.1f}%)')
    log(f'Grade distribution: {stats["grade_distribution"]}')

    # ── 2. EDA Visualizations ───────────────────────────────────────
    print('\n[ Phase 2 ] Generating EDA Visualizations')
    plot_distributions(df, CHART_DIR)
    log('Feature distributions chart saved')
    plot_correlation_heatmap(df, CHART_DIR)
    log('Correlation heatmap saved')
    plot_grade_distribution(df, CHART_DIR)
    log('Grade distribution chart saved')
    plot_risk_distribution(df, CHART_DIR)
    log('Risk distribution chart saved')
    plot_attendance_vs_marks(df, CHART_DIR)
    log('Attendance vs marks scatter saved')
    plot_study_hours_vs_marks(df, CHART_DIR)
    log('Study hours vs marks scatter saved')
    plot_boxplots_by_grade(df, CHART_DIR)
    log('Boxplots by grade saved')
    plot_kpi_summary(df, CHART_DIR)
    log('KPI summary banner saved')

    # ── 3. ML Models ────────────────────────────────────────────────
    print('\n[ Phase 3 ] Training ML Models')

    reg = train_regression_models(df)
    log(f'Regression models trained — Best: {reg["best_model"]} (R²={reg["best_r2"]:.4f})')
    plot_feature_importance(reg['feature_importance'], 'Feature Importance — Regression',
                             CHART_DIR, 'feature_importance_regression.png')
    best_reg_model = reg['trained_models'][reg['best_model']]
    is_linear = reg['best_model'] == 'Linear Regression'
    from ml_models import FEATURES
    import pandas as pd
    X_test = reg['X_test']
    if is_linear:
        preds_reg = reg['trained_models']['Linear Regression'].predict(reg['scaler'].transform(X_test))
    else:
        preds_reg = best_reg_model.predict(X_test)
    plot_regression_results(reg['y_test'].values, preds_reg, CHART_DIR)
    log('Regression charts saved')

    clf = train_classification_models(df)
    log(f'Classification models trained — Best: {clf["best_model"]} (Acc={clf["best_accuracy"]*100:.1f}%)')
    plot_feature_importance(clf['feature_importance'], 'Feature Importance — Classification',
                             CHART_DIR, 'feature_importance_classification.png')
    best_clf = clf['results'][clf['best_model']]
    plot_confusion_matrix(
        np.array(best_clf['Confusion']),
        clf['grade_classes'],
        f'Confusion Matrix — {clf["best_model"]}',
        CHART_DIR
    )
    log('Classification charts saved')

    plot_model_comparison(reg['results'], clf['results'], CHART_DIR)
    log('Model comparison chart saved')

    clustering = train_clustering(df)
    log(f'Clustering complete — {clustering["k"]} clusters: {list(clustering["cluster_sizes"].keys())}')
    plot_clusters(clustering, CHART_DIR)
    log('Cluster visualizations saved')

    # ── 4. Predictions on full dataset ──────────────────────────────
    print('\n[ Phase 4 ] Applying Models to Full Dataset')
    best_rf_reg = reg['trained_models']['Random Forest']
    df['predicted_marks'] = best_rf_reg.predict(df[FEATURES]).round(2)

    best_rf_clf = clf['trained_models']['Random Forest']
    clf_preds = best_rf_clf.predict(df[FEATURES])
    df['predicted_grade'] = clf['label_encoder'].inverse_transform(clf_preds)

    df['cluster_id']   = clustering['df']['cluster_id']
    df['cluster_name'] = clustering['df']['cluster_name']
    log('Predicted semester marks added to dataset')
    log('Predicted grades added to dataset')
    log('Cluster labels added to dataset')

    # ── 5. Save processed dataset ────────────────────────────────────
    processed_path = os.path.join(OUTPUT_DIR, 'student_data_processed.csv')
    df.to_csv(processed_path, index=False)
    log(f'Processed dataset saved → {processed_path}')

    # ── 6. Excel Report ──────────────────────────────────────────────
    print('\n[ Phase 5 ] Generating Excel Report')
    excel_path = os.path.join(OUTPUT_DIR, 'Smart_Campus_Analytics_Report.xlsx')
    generate_excel_report(df, reg['results'], clf['results'], excel_path)
    log(f'Excel report saved → {excel_path}')

    # ── 7. PDF Report ────────────────────────────────────────────────
    print('\n[ Phase 6 ] Generating PDF Executive Report')
    pdf_path = os.path.join(OUTPUT_DIR, 'Smart_Campus_Analytics_Report.pdf')
    generate_pdf_report(df, reg['results'], clf['results'], clustering, CHART_DIR, pdf_path)
    log(f'PDF report saved → {pdf_path}')

    # ── Summary ──────────────────────────────────────────────────────
    elapsed = time.time() - t0
    print('\n' + '='*60)
    print(f'  PIPELINE COMPLETE  ({elapsed:.1f}s)')
    print('='*60)
    print(f'\n  Outputs generated:')
    print(f'      Excel Report  →  outputs/Smart_Campus_Analytics_Report.xlsx')
    print(f'      PDF Report    →  outputs/Smart_Campus_Analytics_Report.pdf')
    print(f'      CSV Dataset   →  outputs/student_data_processed.csv')
    print(f'       Charts        →  outputs/charts/ ({len(os.listdir(CHART_DIR))} files)')
    print()
    print(f'  Key Findings:')
    print(f'    • Total students:   {len(df)}')
    print(f'    • At-risk students: {stats["at_risk_count"]} ({stats["at_risk_count"]/len(df)*100:.1f}%)')
    print(f'    • Critical risk:    {int((df["risk_tier"]=="Critical").sum())}')
    print(f'    • Best regression:  {reg["best_model"]} (R²={reg["best_r2"]:.4f})')
    print(f'    • Best classifier:  {clf["best_model"]} ({clf["best_accuracy"]*100:.1f}% acc)')
    print()

    return df, reg, clf, clustering


if __name__ == '__main__':
    run()
