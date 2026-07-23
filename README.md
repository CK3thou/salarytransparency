## Running locally

This project now runs as a local browser-based app on your machine.

### Requirements
- Python 3.11+
- Dependencies from `requirements.txt`

### Start the app
```sh
pip install -r requirements.txt
python main.py
```

Then open:
```text
http://127.0.0.1:8000
```

You can:
- view salary summaries
- browse recent entries
- submit new salary data

If you prefer the old terminal experience, run:
```sh
python main.py --cli
```

### Docker
A Docker setup is still available, but the default local workflow is the browser app above.