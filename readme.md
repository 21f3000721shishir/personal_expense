# Expense Tracker

A simple personal finance tool to record and review expenses with a Flask backend and Streamlit frontend.

## Overview

You are on a team building a small personal finance tool. As a user, I can record and review my personal expenses so I can understand where my money is going. This tool is designed to work in real-world conditions (unreliable networks, browser refreshes, retries).

## Features

- ✅ Create expense entries with amount, category, description, and date
- ✅ View all expenses in a list
- ✅ Filter expenses by category
- ✅ Sort expenses by date (newest first)
- ✅ View total expenses for filtered results
- ✅ Idempotent expense creation (safe retries on network issues)

## Tech Stack

**Backend:**
- Flask - REST API framework
- Flask-CORS - Cross-origin resource sharing
- Gunicorn - Production WSGI server

**Frontend:**
- Streamlit - Web UI framework
- Pandas - Data manipulation
- Plotly - Data visualization
- Requests - HTTP client

## Requirements

Create a `requirements.txt` file with:

```
flask
flask-cors
streamlit
requests
pandas
gunicorn
plotly
```

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository
```bash
git clone <repository-url>
cd expense-tracker
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

## Running Locally

### Backend
```bash
# Development
python app.py

# Production (with Gunicorn)
gunicorn app:app
```

The API will be available at `http://localhost:5000`

### Frontend
```bash
streamlit run frontend.py
```

The UI will be available at `http://localhost:8501`

## API Documentation

### POST /expenses
Create a new expense entry.

**Request Body:**
```json
{
  "amount": 1500,
  "category": "Food",
  "description": "Lunch at restaurant",
  "date": "2026-01-21"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid-string",
  "amount": 1500,
  "category": "Food",
  "description": "Lunch at restaurant",
  "date": "2026-01-21",
  "created_at": "2026-01-21T10:30:00"
}
```

### GET /expenses
Retrieve expenses with optional filtering and sorting.

**Query Parameters:**
- `category` (optional) - Filter by category
- `sort` (optional) - Sort order: `date_desc` for newest first

**Examples:**
```bash
# Get all expenses
GET /expenses

# Filter by category
GET /expenses?category=Food

# Sort by newest first
GET /expenses?sort=date_desc

# Filter and sort
GET /expenses?category=Food&sort=date_desc
```

**Response (200 OK):**
```json
{
  "expenses": [
    {
      "id": "uuid-1",
      "amount": 1500,
      "category": "Food",
      "description": "Lunch",
      "date": "2026-01-21"
    }
  ],
  "total": 1500,
  "count": 1
}
```

## Deployment

### Backend Deployment (Railway)

1. Create a new project on [Railway](https://railway.app)
2. Connect your GitHub repository
3. Railway will auto-detect your Python app
4. Set the start command (if needed):
   ```
   gunicorn app:app --bind 0.0.0.0:$PORT
   ```
5. Deploy and note your backend URL (e.g., `https://your-app.railway.app`)

### Frontend Deployment

1. Update the `API_URL` in `frontend.py` with your Railway backend URL:
   ```python
   API_URL = "https://your-app.railway.app"
   ```

2. Deploy frontend using [Streamlit Cloud](https://streamlit.io/cloud):
   - Connect your GitHub repository
   - Select `frontend.py` as the main file
   - Deploy

## Project Structure

```
expense-tracker/
├── app.py              # Flask backend API
├── frontend.py         # Streamlit frontend UI
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Design Decisions

### Idempotency
- POST requests use request fingerprinting to prevent duplicate entries on network retries
- Combines amount, category, description, and date to create unique request identifier
- Returns existing expense if duplicate detected

### Data Storage
- In-memory storage for simplicity (suitable for demo/development)
- For production, migrate to PostgreSQL, MongoDB, or SQLite

### Error Handling
- Comprehensive input validation
- Graceful error responses with appropriate HTTP status codes
- User-friendly error messages

### CORS Configuration
- Enabled for cross-origin requests
- Allows frontend-backend communication across different domains

## Acceptance Criteria

All acceptance criteria met:

1. ✅ User can create a new expense entry with amount, category, description, and date
2. ✅ User can view a list of expenses
3. ✅ User can filter expenses by category
4. ✅ User can sort expenses by date (newest first)
5. ✅ User can see a simple total of expenses for the current list (e.g., "Total: ₹X")

## Future Enhancements

- [ ] Persistent database (PostgreSQL/MongoDB)
- [ ] User authentication and authorization
- [ ] Edit and delete expense functionality
- [ ] Budget tracking and alerts
- [ ] Export to CSV/PDF
- [ ] Multi-currency support
- [ ] Custom expense categories
- [ ] Date range filtering
- [ ] Analytics dashboard with charts
- [ ] Mobile responsive design
- [ ] Recurring expenses
- [ ] Receipt image upload

## Troubleshooting

### CORS Issues
If you encounter CORS errors, ensure:
- Flask-CORS is properly installed
- Backend allows requests from frontend origin
- Check browser console for specific errors

### Connection Refused
- Verify backend is running on correct port
- Check API_URL in frontend matches backend URL
- Ensure no firewall blocking connections

### Railway Deployment Issues
- Check Railway logs for errors
- Verify `requirements.txt` includes all dependencies
- Ensure Gunicorn is specified for production

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - feel free to use this project for learning and development.

## Contact

For questions or support, please open an issue in the repository.

---

**Note:** This is a minimal implementation designed for learning and demonstration. For production use, implement proper database persistence, authentication, and security measures.