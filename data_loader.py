import pandas as pd

# ── Column name mapping ─────────────────────────────────────────────────────────
# Maps your full bilingual survey headers to short readable keys used in the code.
# If Excel truncated any headers, adjust the right-hand side to match exactly.

SURVEY_COLS = {
    "gender":               "Gender / الجنس",
    "age_range":            "Age Range / المرحلة العمرية",
    "education":            "What is your highest level of education? / ماهو أعلى مستوى تعليمي لديك؟",
    "field_of_study":       "What's your field of study? / ماهو تخصصك؟",
    "has_work_experience":  "Do you have previous work experience? / هل لديك خبرة عمل سابقة؟",
    "main_sector":          "If yes, then in which main sector? / اذا كان الجواب نعم، في أي قطاع رئيسي؟",
    "specific_sector":      "In which specific sector? / في أي قطاع بالتحديد؟",
    "job_satisfaction":     "How satisfied are you with your current job? / مامدى رضاك عن وظيفتك الحالية؟",
    "job_matches_skills":   "Does your job match your skills and qualifications? / هل وظيفتك تتناسب مع مهاراتك و مؤهلاتك؟",
    "daily_work_hours":     "How many hours do you work per day? / عدد ساعات العمل يوميًا؟",
    "shift_type":           "Night or day shift? / ساعات عمل صباحية أم مسائية؟",
    "hours_suit_lifestyle": "Are your working hours suitable for your lifestyle? / هل ساعات عملك تتناسب مع نمط حياتك؟",
    "training_provided":    "Does your company provide training or development opportunities? / هل توفر جهة عملك فرص تدريب أو تطوير؟",
    "promotion_opps":       "Do you see opportunities for promotion in your job? / هل ترى فرصًا للترقية في وظيفتك؟",
    "job_stability":        "Do you feel your job is stable long-term? / هل تشعر بالإستقرار في عملك على المدى البعيد؟",
    "job_choice_factors":   "What 3 factors influence your choice of job the most? / ماهي أكثر ثلاثة عوامل تأثر على اختيارك للوظيفة الآن او مستقبلًا بشكل كبير؟",
    "preferred_job_type":   "Which would you choose? / أي من الخيارات الآتية قد تختار؟",
    "job_refusal_reasons":  "What would make you refuse a job even if the salary is acceptable? / أي من هذه الخيارات قد تجعلك ترفض وظيفة حتى مع راتب مناسب؟",
    "consider_industrial":  "Would you consider working in a manufacturing or industrial job? / هل تفكر في العمل في مجال الصناعة؟",
    "industrial_concerns":  "What are your concerns about working in industrial/manufacturing jobs? / ما هي مخاوفك بشأن العمل في الوظائف الصناعية/التصنيعية؟",
    "saudization_impact":   "Has Saudization improved job opportunities in your sector? / هل ساهمت السعودة على تحسين فرص العمل في قطاعك؟",
}

# Columns to drop — not analytically useful
DROP_COLS = ["Id", "Start time", "Completion time", "Email", "Name"]


def load_survey(path="data/survey.csv"):
    df = pd.read_csv(path)
    df = df.drop(columns=[c for c in DROP_COLS if c in df.columns], errors="ignore")
    reverse_map = {v: k for k, v in SURVEY_COLS.items()}
    df = df.rename(columns={col: reverse_map[col] for col in df.columns if col in reverse_map})
    return df


def load_labor_market(path="data/labor_market.csv"):
    """
    Your labor market CSV with Saudi vs non-Saudi percentages per sector.
    Expected columns: sector, saudi_pct, non_saudi_pct
    Adjust if your headers differ.
    """
    df = pd.read_csv(path)
    return df


def _top_values(series, n=5):
    return series.dropna().value_counts().head(n).index.tolist()


def build_sector_summary():
    """
    Builds the full text context injected into the AI system prompt.
    """
    lines = []

    # ── Part 1: Labor market data ───────────────────────────────────────────────
    try:
        labor_df = load_labor_market()
        lines.append("=== LABOR MARKET DATA (Saudization rates by sector) ===\n")
        lines.append(labor_df.to_string(index=False))
        lines.append("")
    except FileNotFoundError:
        lines.append("[labor_market.csv not found — skipping]\n")
    except Exception as e:
        lines.append(f"[Error loading labor market data: {e}]\n")

    # ── Part 2: Survey overview ─────────────────────────────────────────────────
    try:
        df = load_survey()
        total = len(df)
        lines.append(f"=== SURVEY DATA OVERVIEW (n={total} respondents) ===\n")

        for col, label in [("gender", "Gender"), ("age_range", "Age range"), ("education", "Education level")]:
            if col in df.columns:
                lines.append(f"{label} breakdown:")
                lines.append(df[col].value_counts().to_string())
                lines.append("")

        # ── Part 3: Per-sector breakdown ────────────────────────────────────────
        sector_col = "main_sector" if "main_sector" in df.columns else None
        if sector_col:
            lines.append("=== SURVEY INSIGHTS BY SECTOR ===\n")

            for sector in df[sector_col].dropna().unique():
                sdf = df[df[sector_col] == sector]
                n = len(sdf)
                lines.append(f"--- Sector: {sector} (n={n}) ---")

                # Simple value_counts for each relevant column
                simple_cols = {
                    "job_satisfaction":     "Job satisfaction scores",
                    "job_matches_skills":   "Job matches skills",
                    "daily_work_hours":     "Daily work hours",
                    "shift_type":           "Shift type",
                    "hours_suit_lifestyle": "Hours suit lifestyle",
                    "training_provided":    "Training provided by employer",
                    "promotion_opps":       "Sees promotion opportunities",
                    "job_stability":        "Feels job is stable long-term",
                    "consider_industrial":  "Would consider industrial work",
                    "saudization_impact":   "Believes Saudization improved opportunities",
                    "preferred_job_type":   "Preferred job type",
                }
                for col, label in simple_cols.items():
                    if col in sdf.columns:
                        lines.append(f"  {label}:")
                        lines.append(sdf[col].value_counts().to_string())

                # Top responses for open/multi-select columns
                for col, label in [
                    ("job_choice_factors", "Top job choice factors"),
                    ("job_refusal_reasons", "Top job refusal reasons"),
                    ("industrial_concerns", "Top concerns about industrial work"),
                ]:
                    if col in sdf.columns:
                        lines.append(f"  {label}:")
                        for val in _top_values(sdf[col], n=5):
                            lines.append(f"    - {val}")

                lines.append("")

        # ── Part 4: Overall cross-sector patterns ───────────────────────────────
        lines.append("=== OVERALL PATTERNS (all respondents) ===\n")

        for col, label in [
            ("job_choice_factors",  "Most common job choice factors"),
            ("job_refusal_reasons", "Most common job refusal reasons"),
            ("industrial_concerns", "Most common industrial job concerns"),
        ]:
            if col in df.columns:
                lines.append(f"{label}:")
                for val in _top_values(df[col], n=8):
                    lines.append(f"  - {val}")
                lines.append("")

        for col, label in [
            ("consider_industrial", "Overall interest in industrial work"),
            ("saudization_impact",  "Overall perception of Saudization impact"),
        ]:
            if col in df.columns:
                lines.append(f"{label}:")
                lines.append(df[col].value_counts().to_string())
                lines.append("")

    except FileNotFoundError:
        lines.append("[survey.csv not found — skipping survey data]\n")
    except Exception as e:
        lines.append(f"[Error loading survey data: {e}]\n")

    return "\n".join(lines)