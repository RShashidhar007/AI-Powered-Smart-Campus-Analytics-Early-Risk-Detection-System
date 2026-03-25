import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
import os
PALETTE   = ['#2E86AB', '#E84855', '#F4A261', '#2EC4B6', '#9B59B6', '#27AE60']
RISK_COLORS = {
    'Low':      '#27AE60',
    'Moderate': '#F39C12',
    'High':     '#E67E22',
    'Critical': '#E74C3C',
}
GRADE_COLORS = {
    'A': '#27AE60', 'B': '#2E86AB', 'C': '#F4A261',
    'D': '#E67E22', 'F': '#E74C3C',
}
def _save(fig, path, dpi=150):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return path
def setup_style():
    sns.set_theme(style='whitegrid', palette=PALETTE)
    plt.rcParams.update({
        'font.family': 'DejaVu Sans',
        'axes.titlesize': 13,
        'axes.labelsize': 11,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
    })
def plot_distributions(df, out_dir):
    setup_style()
    cols = ['attendance', 'internal_marks', 'assignment_score',
            'quiz_score', 'lab_marks', 'semester_marks', 'study_hours']
    fig, axes = plt.subplots(2, 4, figsize=(18, 8))
    axes = axes.flatten()
    for i, col in enumerate(cols):
        axes[i].hist(df[col], bins=25, color=PALETTE[i % len(PALETTE)], edgecolor='white', alpha=0.9)
        axes[i].axvline(df[col].mean(), color='red', linestyle='--', linewidth=1.5, label=f'Mean: {df[col].mean():.1f}')
        axes[i].set_title(col.replace('_', ' ').title())
        axes[i].legend(fontsize=8)
    axes[-1].set_visible(False)
    fig.suptitle('Feature Distributions — {len(df)} Students', fontsize=15, fontweight='bold', y=1.01)
    fig.tight_layout()
    return _save(fig, f'{out_dir}/distributions.png')
def plot_correlation_heatmap(df, out_dir):
    setup_style()
    numeric_cols = ['attendance', 'internal_marks', 'assignment_score',
                    'quiz_score', 'lab_marks', 'semester_marks', 'study_hours', 'risk_score']
    corr = df[numeric_cols].corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdYlGn',
                center=0, ax=ax, linewidths=0.5,
                annot_kws={'size': 9}, vmin=-1, vmax=1)
    ax.set_title('Correlation Matrix — Academic Features', fontsize=14, fontweight='bold', pad=15)
    fig.tight_layout()
    return _save(fig, f'{out_dir}/correlation_heatmap.png')
def plot_grade_distribution(df, out_dir):
    setup_style()
    grade_counts = df['grade_label'].value_counts().reindex(['A', 'B', 'C', 'D', 'F'])
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    bars = ax1.bar(grade_counts.index,
                   grade_counts.values,
                   color=[GRADE_COLORS[g] for g in grade_counts.index],
                   edgecolor='white', linewidth=1.2)
    for bar, val in zip(bars, grade_counts.values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                 str(val), ha='center', va='bottom', fontweight='bold', fontsize=11)
    ax1.set_title('Grade Distribution (Count)', fontweight='bold')
    ax1.set_xlabel('Grade'); ax1.set_ylabel('Number of Students')
    wedges, texts, autotexts = ax2.pie(
        grade_counts.values,
        labels=grade_counts.index,
        colors=[GRADE_COLORS[g] for g in grade_counts.index],
        autopct='%1.1f%%', startangle=140,
        wedgeprops=dict(edgecolor='white', linewidth=1.5)
    )
    for at in autotexts:
        at.set_fontsize(10)
    ax2.set_title('Grade Distribution (%)', fontweight='bold')

    fig.suptitle('Student Grade Distribution', fontsize=14, fontweight='bold')
    fig.tight_layout()
    return _save(fig, f'{out_dir}/grade_distribution.png')
def plot_risk_distribution(df, out_dir):
    setup_style()
    risk_counts = df['risk_tier'].value_counts().reindex(['Low', 'Moderate', 'High', 'Critical'])
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(risk_counts.index,
                   risk_counts.values,
                   color=[RISK_COLORS[r] for r in risk_counts.index],
                   edgecolor='white', linewidth=1.2, height=0.55)
    for bar, val in zip(bars, risk_counts.values):
        pct = val / len(df) * 100
        ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                f'{val} ({pct:.1f}%)', va='center', fontsize=10, fontweight='bold')
    ax.set_xlim(0, risk_counts.max() * 1.25)
    ax.set_title('Student Risk Tier Distribution', fontsize=14, fontweight='bold')
    ax.set_xlabel('Number of Students')
    fig.tight_layout()
    return _save(fig, f'{out_dir}/risk_distribution.png')
def plot_attendance_vs_marks(df, out_dir):
    setup_style()
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(df['attendance'], df['semester_marks'],
                         c=df['risk_score'], cmap='RdYlGn_r',
                         alpha=0.7, s=40, edgecolors='white', linewidths=0.3)
    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label('Risk Score', fontsize=10)
    # Trend line
    z = np.polyfit(df['attendance'], df['semester_marks'], 1)
    p = np.poly1d(z)
    xline = np.linspace(df['attendance'].min(), df['attendance'].max(), 200)
    ax.plot(xline, p(xline), 'navy', linewidth=2, linestyle='--', label='Trend')
    ax.axvline(65, color='red', linestyle=':', linewidth=1.5, label='65% Attendance Threshold')
    ax.set_xlabel('Attendance (%)', fontsize=11)
    ax.set_ylabel('Semester Marks', fontsize=11)
    ax.set_title('Attendance vs Semester Marks (colored by Risk Score)', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)
    fig.tight_layout()
    return _save(fig, f'{out_dir}/attendance_vs_marks.png')
def plot_study_hours_vs_marks(df, out_dir):
    setup_style()
    fig, ax = plt.subplots(figsize=(10, 6))
    for grade in ['A', 'B', 'C', 'D', 'F']:
        sub = df[df['grade_label'] == grade]
        ax.scatter(sub['study_hours'], sub['semester_marks'],
                   label=f'Grade {grade}', color=GRADE_COLORS[grade],
                   alpha=0.7, s=45, edgecolors='white', linewidths=0.3)
    ax.set_xlabel('Study Hours per Day', fontsize=11)
    ax.set_ylabel('Semester Marks', fontsize=11)
    ax.set_title('Study Hours vs Semester Marks (by Grade)', fontsize=13, fontweight='bold')
    ax.legend(title='Grade', fontsize=9)
    fig.tight_layout()
    return _save(fig, f'{out_dir}/study_hours_vs_marks.png')
def plot_boxplots_by_grade(df, out_dir):
    setup_style()
    metrics = ['attendance', 'internal_marks', 'study_hours', 'assignment_score']
    fig, axes = plt.subplots(1, 4, figsize=(16, 6))
    for ax, metric in zip(axes, metrics):
        data_by_grade = [df[df['grade_label'] == g][metric].values for g in ['A', 'B', 'C', 'D', 'F']]
        bp = ax.boxplot(data_by_grade, patch_artist=True,
                        medianprops=dict(color='black', linewidth=2))
        for patch, grade in zip(bp['boxes'], ['A', 'B', 'C', 'D', 'F']):
            patch.set_facecolor(GRADE_COLORS[grade])
            patch.set_alpha(0.8)
        ax.set_xticklabels(['A', 'B', 'C', 'D', 'F'])
        ax.set_title(metric.replace('_', ' ').title(), fontweight='bold')
        ax.set_xlabel('Grade')
    fig.suptitle('Feature Distribution by Grade', fontsize=14, fontweight='bold')
    fig.tight_layout()
    return _save(fig, f'{out_dir}/boxplots_by_grade.png')
def plot_feature_importance(feat_imp: dict, title: str, out_dir: str, fname: str):
    setup_style()
    items = sorted(feat_imp.items(), key=lambda x: x[1])
    labels = [k.replace('_', ' ').title() for k, _ in items]
    values = [v for _, v in items]
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(labels, values, color=PALETTE[:len(values)], edgecolor='white')
    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height()/2,
                f'{val:.3f}', va='center', fontsize=9, fontweight='bold')
    ax.set_xlim(0, max(values) * 1.2)
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.set_xlabel('Feature Importance Score')
    fig.tight_layout()
    return _save(fig, f'{out_dir}/{fname}')
def plot_regression_results(y_test, predictions, out_dir):
    setup_style()
    from sklearn.metrics import r2_score
    r2 = r2_score(y_test, predictions)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    axes[0].scatter(y_test, predictions, alpha=0.6, color=PALETTE[0], s=40, edgecolors='white')
    mn, mx = min(y_test.min(), predictions.min()), max(y_test.max(), predictions.max())
    axes[0].plot([mn, mx], [mn, mx], 'r--', linewidth=2, label='Perfect Fit')
    axes[0].set_xlabel('Actual Semester Marks'); axes[0].set_ylabel('Predicted Semester Marks')
    axes[0].set_title(f'Actual vs Predicted  (R² = {r2:.3f})', fontweight='bold')
    axes[0].legend()

    residuals = np.array(y_test) - np.array(predictions)
    axes[1].scatter(predictions, residuals, alpha=0.6, color=PALETTE[2], s=40, edgecolors='white')
    axes[1].axhline(0, color='red', linestyle='--', linewidth=2)
    axes[1].set_xlabel('Predicted Values'); axes[1].set_ylabel('Residuals')
    axes[1].set_title('Residual Plot', fontweight='bold')

    fig.suptitle('Regression Model Performance', fontsize=14, fontweight='bold')
    fig.tight_layout()
    return _save(fig, f'{out_dir}/regression_results.png')
def plot_confusion_matrix(cm, classes, title, out_dir):
    setup_style()
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cm, interpolation='nearest', cmap='Blues')
    plt.colorbar(im, ax=ax)
    ax.set_xticks(range(len(classes))); ax.set_yticks(range(len(classes)))
    ax.set_xticklabels(classes); ax.set_yticklabels(classes)
    thresh = cm.max() / 2
    for i in range(len(classes)):
        for j in range(len(classes)):
            ax.text(j, i, str(cm[i][j]), ha='center', va='center',
                    color='white' if cm[i][j] > thresh else 'black', fontsize=11, fontweight='bold')
    ax.set_ylabel('True Grade', fontsize=11); ax.set_xlabel('Predicted Grade', fontsize=11)
    ax.set_title(title, fontsize=13, fontweight='bold')
    fig.tight_layout()
    return _save(fig, f'{out_dir}/confusion_matrix.png')
def plot_model_comparison(reg_results: dict, clf_results: dict, out_dir: str):
    setup_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    names_r = list(reg_results.keys())
    r2s     = [reg_results[n]['R2'] for n in names_r]
    bars = ax1.bar(names_r, r2s, color=PALETTE[:len(names_r)], edgecolor='white')
    for bar, val in zip(bars, r2s):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                 f'{val:.3f}', ha='center', fontweight='bold', fontsize=10)
    ax1.set_ylim(0, 1.1); ax1.set_ylabel('R² Score')
    ax1.set_title('Regression: R² Comparison', fontweight='bold')
    ax1.tick_params(axis='x', rotation=10)
    # Classification Accuracy
    names_c = list(clf_results.keys())
    accs    = [clf_results[n]['Accuracy'] for n in names_c]
    bars2 = ax2.bar(names_c, accs, color=PALETTE[:len(names_c)], edgecolor='white')
    for bar, val in zip(bars2, accs):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                 f'{val:.3f}', ha='center', fontweight='bold', fontsize=10)
    ax2.set_ylim(0, 1.1); ax2.set_ylabel('Accuracy')
    ax2.set_title('Classification: Accuracy Comparison', fontweight='bold')
    ax2.tick_params(axis='x', rotation=10)

    fig.suptitle('Model Performance Comparison', fontsize=14, fontweight='bold')
    fig.tight_layout()
    return _save(fig, f'{out_dir}/model_comparison.png')


def plot_clusters(clustering_result: dict, out_dir: str):
    setup_style()
    df      = clustering_result['df']
    cluster_colors = ['#27AE60', '#F39C12', '#E74C3C', '#9B59B6', '#2E86AB']

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Scatter: attendance vs semester_marks
    unique_clusters = sorted(df['cluster_name'].unique())
    for i, cname in enumerate(unique_clusters):
        sub = df[df['cluster_name'] == cname]
        axes[0].scatter(sub['attendance'], sub['semester_marks'],
                        color=cluster_colors[i % len(cluster_colors)],
                        label=cname, alpha=0.7, s=45, edgecolors='white', linewidths=0.3)
    axes[0].set_xlabel('Attendance (%)'); axes[0].set_ylabel('Semester Marks')
    axes[0].set_title('Student Clusters: Attendance vs Marks', fontweight='bold')
    axes[0].legend(fontsize=8, title='Cluster')

    # Cluster profile bar chart
    profile = clustering_result['cluster_profiles'].copy()
    # Drop duplicate columns if any
    profile = profile.loc[:, ~profile.columns.duplicated()]
    features = ['attendance', 'semester_marks', 'study_hours']
    x = np.arange(len(profile))
    width = 0.25
    for i, feat in enumerate(features):
        vals = profile[feat].values.astype(float)
        norm_vals = vals / vals.max() * 100
        axes[1].bar(x + i * width, norm_vals, width, label=feat.replace('_', ' ').title(),
                    color=PALETTE[i % len(PALETTE)], edgecolor='white', alpha=0.85)
    axes[1].set_xticks(x + width)
    axes[1].set_xticklabels(profile['cluster_name'].values, rotation=15, ha='right', fontsize=8)
    axes[1].set_ylabel('Normalized Score (0–100)')
    axes[1].set_title('Cluster Profiles Comparison', fontweight='bold')
    axes[1].legend(fontsize=8)

    fig.suptitle('Student Clustering Analysis', fontsize=14, fontweight='bold')
    fig.tight_layout()
    return _save(fig, f'{out_dir}/clusters.png')


def plot_kpi_summary(df, out_dir):
    """Banner-style KPI summary chart for reports."""
    setup_style()
    total     = len(df)
    at_risk   = df['is_at_risk'].sum()
    avg_marks = df['semester_marks'].mean()
    avg_att   = df['attendance'].mean()
    grade_a   = (df['grade_label'] == 'A').sum()

    kpis = [
        ('Total Students', str(total),          '#2E86AB'),
        ('At-Risk Students', str(at_risk),       '#E74C3C'),
        ('Avg Semester Marks', f'{avg_marks:.1f}','#27AE60'),
        ('Avg Attendance', f'{avg_att:.1f}%',    '#F39C12'),
        ('Grade A Students', str(grade_a),        '#9B59B6'),
    ]

    fig, axes = plt.subplots(1, 5, figsize=(16, 3))
    for ax, (label, value, color) in zip(axes, kpis):
        ax.set_facecolor(color)
        ax.text(0.5, 0.6, value, ha='center', va='center',
                fontsize=26, fontweight='bold', color='white',
                transform=ax.transAxes)
        ax.text(0.5, 0.2, label, ha='center', va='center',
                fontsize=9, color='white', alpha=0.9,
                transform=ax.transAxes, wrap=True)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_edgecolor('white')
            spine.set_linewidth(2)

    fig.suptitle('Key Performance Indicators', fontsize=13, fontweight='bold', y=1.05)
    fig.tight_layout()
    return _save(fig, f'{out_dir}/kpi_summary.png')
