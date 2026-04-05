import logging
import json
from config import load_config
from checker import run_checklist, simulate_incident, generate_report

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

 def main():
    try:
        config = load_config()
        logger.info('Loaded config')

        # Run checklist evaluation
        scores = run_checklist(config)
        logger.info(f'Checklist scores: {scores}')

        # Simulate incident
        incident_result = simulate_incident(config)
        logger.info(f'Incident simulation: {incident_result}')

        # Generate report
        report = generate_report(scores, incident_result)
        print(json.dumps(report, indent=2))

    except Exception as e:
        logger.error(f'Error running checker: {e}')
        raise

if __name__ == '__main__':
    main()
