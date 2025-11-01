# AI Agent Instructions for Salary Transparency Platform

This document guides AI agents working in the salary transparency platform codebase.

## Project Overview

A Streamlit-based web application that collects and visualizes salary data, with:
- Mobile-first responsive design
- PWA (Progressive Web App) capabilities
- Data persistence in CSV/Excel formats
- Interactive visualizations using Plotly
- Currency conversion features

## Key Components & Data Flow

```
main.py                 # App entry point & UI layout
├── components/         # Reusable UI components
│   ├── filters.py     # Data filtering controls
│   └── forms.py       # Salary submission form
├── utils/             # Core business logic
│   ├── data_handler.py    # Data loading/saving
│   └── visualizations.py  # Plotly chart generation
├── data/              # Data storage
│   └── salary_data.csv    # Primary dataset
└── static/            # PWA assets
    ├── manifest.json
    └── sw.js
```

Data flow:
1. `data_handler.py` loads salary data from CSV/Excel
2. User inputs via `forms.py` are validated and saved
3. `visualizations.py` transforms data into Plotly charts
4. `main.py` orchestrates components and manages layout

## Development Workflows

### Running the App

```bash
# Install dependencies
pip install -r requirements.txt

# Start the app (MUST use streamlit run, not python directly)
streamlit run main.py
```

Note: Running `python main.py` directly will show an error message - the app requires Streamlit's runtime context.

### Data Handling Patterns

- Salary data is stored in both CSV and Excel formats for redundancy
- New submissions are appended to existing data
- Currency conversion (ZMW ↔ USD) uses forex-python (gracefully degrades if unavailable)
- Data cleaning normalizes column names and handles missing values

Example from `data_handler.py`:
```python
df['Years of Experience'] = df['Years of Experience'].str.extract(r'(\d+)', expand=False)
```

### UI Component Conventions

1. All visualizations are responsive and mobile-first
2. Forms use Streamlit columns for better mobile layout
3. Charts are wrapped in tabs for organization
4. Custom CSS handles mobile breakpoints (768px)

### Key Dependencies

- `streamlit>=1.32.0`: Core framework
- `pandas>=2.2.0`: Data handling
- `plotly>=5.18.0`: Visualizations
- `forex-python>=1.9.0`: Currency conversion (optional)

## Integration Points

1. Currency conversion via forex-python API
2. PWA service worker for offline capability
3. File system for data persistence
4. Plotly for interactive visualizations

## Testing & Debugging

- Check warnings in the Streamlit server output
- Monitor data file operations in `data/` directory
- Use sidebar data preview toggles for debugging
- Watch for currency conversion failures (degrades gracefully)

## Common Pitfalls

1. Don't run `python main.py` directly - use `streamlit run`
2. Don't modify column names in `salary_data.csv` - they're hardcoded in transforms
3. Remember to handle both CSV and Excel data sources
4. Test mobile layouts - the app is mobile-first
5. Wrap Streamlit-specific code in runtime checks