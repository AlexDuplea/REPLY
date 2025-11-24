# Wellness Journal Application

A personal journaling web app that tracks your writing habits, visualizes sentiment trends, and provides insightful statistics.

## Features

- **Diary Entries**: Write and store daily journal entries.
- **Stats Dashboard**: View overview cards, insights, line charts (Stress, Happiness, Energy), radar chart, heatmap, and milestones.
- **Export**: Export entries as CSV or PDF.
- **Responsive Design**: Works on desktop and mobile devices.
- **Back Button**: Easy navigation from the stats page back to the diary.

## Tech Stack

- **Backend**: Flask (Python) – API endpoints for entries and stats.
- **Frontend**: HTML, CSS (vanilla), JavaScript (Chart.js for visualizations).
- **Design**: Modern, premium UI with glass‑morphism, micro‑animations, and a cohesive color palette.

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repo-directory>
   ```
2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the development server**
   ```bash
   flask run
   ```
   The app will be available at `http://127.0.0.1:5000/`.

## Usage

- Navigate to the home page to start writing journal entries.
- Visit `/stats` to see the statistics dashboard.
- Use the **Back** button in the header to return to the diary.
- Adjust the time filter (7 Days, 30 Days, 3 Months, All) to change the chart data range.
- Export your data via the PDF or CSV buttons.

## Development

- **CSS**: Styles are located in `static/css/`. The `stats.css` file contains page‑specific styling.
- **JS**: Core logic resides in `static/js/stats.js`.
- **Templates**: HTML templates are in the `templates/` folder (`stats.html`, `base.html`, etc.).

## Contributing

Feel free to open issues or submit pull requests. Please follow the existing code style and run linting tools before committing.

## License

This project is licensed under the MIT License.
