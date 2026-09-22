"""
Master pipeline execution script orchestrating:
Prepare Data -> Prepare Models/Artifacts -> Evaluate Models -> Generate Reports
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.logging_config import logger
from scripts.prepare_data import main as prepare_data_main
from scripts.train_all_models import main as train_all_main
from scripts.evaluate_models import main as evaluate_main
from scripts.generate_reports import main as reports_main


def main():
    logger.info("=====================================================")
    logger.info("  STARTING COMPLETE PIPELINE EXECUTION")
    logger.info("  AI Meeting Action-Item Extractor")
    logger.info("=====================================================")

    try:
        logger.info("[Step 1/4] Running prepare_data.py...")
        prepare_data_main()

        logger.info("[Step 2/4] Running train_all_models.py...")
        train_all_main()

        logger.info("[Step 3/4] Running evaluate_models.py...")
        evaluate_main()

        logger.info("[Step 4/4] Running generate_reports.py...")
        reports_main()

        logger.info("=====================================================")
        logger.info("  PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
        logger.info("=====================================================")
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
