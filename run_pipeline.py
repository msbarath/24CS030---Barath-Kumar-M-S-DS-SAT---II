"""Main pipeline — runs all phases in sequence."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_inspection import run_inspection, write_inspection_report
from src.preprocessing import run_preprocessing
from src.analysis import run_eda
from src.modeling import run_modeling
from src.export_reports import create_excel, create_pptx


def main():
    print("=" * 60)
    print("PHASE A — Data Inspection")
    print("=" * 60)
    results, _ = run_inspection()
    write_inspection_report(results)

    print("\n" + "=" * 60)
    print("PHASE B & C — Preprocessing and Integration")
    print("=" * 60)
    integrated, audits = run_preprocessing()

    print("\n" + "=" * 60)
    print("PHASE D — Exploratory Data Analysis")
    print("=" * 60)
    eda_results = run_eda()

    print("\n" + "=" * 60)
    print("PHASE E & F — Feature Engineering and Modeling")
    print("=" * 60)
    model_results = run_modeling()

    print("\n" + "=" * 60)
    print("PHASE G — Excel Workbook")
    print("=" * 60)
    create_excel(eda_results)

    print("\n" + "=" * 60)
    print("PHASE I — PowerPoint Presentation")
    print("=" * 60)
    create_pptx(eda_results, model_results)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    return eda_results, model_results


if __name__ == "__main__":
    main()
