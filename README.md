# English Vocabulary Backend

A FastAPI-based backend service for managing English vocabulary words and high scores. This API allows users to create, read, and update vocabulary entries, as well as track high scores for vocabulary-related activities.

## Features

- Vocabulary Management
  - Create new vocabulary entries
  - Retrieve all vocabulary entries
  - Update existing vocabulary entries
  - Search for specific words

- High Score System
  - Track user scores
  - Retrieve high scores
  - Get all-time leaderboard

## Technology Stack

- Python 3.13
- FastAPI
- SQLAlchemy (ORM)
- SQLite (Database)
- Uvicorn (ASGI Server)
- Pydantic (Data Validation)

## Getting Started

### Prerequisites

- Python 3.13 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. Clone the repository
```bash
git clone https://github.com/r00kieAd/english_vocab_backend.git
cd english_vocab_backend
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Start the server
```bash
cd server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

After starting the server, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Vocabulary Endpoints

- `GET /vocabs/read` - Get all vocabulary entries
- `POST /vocabs/create` - Add a new vocabulary entry
- `PUT /vocabs/update/{word}` - Update an existing vocabulary entry

Example vocabulary entry:
```json
{
    "word": "ardent",
    "word_type": "adjective",
    "meaning": "Very passionate or enthusiastic",
    "example": "He is an ardent supporter of environmental causes."
}
```

### Score Endpoints

- `GET /scores/all_scores` - Get all scores (leaderboard)
- `GET /scores/high_score` - Get the highest score
- `POST /scores/insert_score` - Add a new score entry

Example score entry:
```json
{
    "high_score": 100,
    "high_scorer": "Player1"
}
```

## Project Structure

```
server/
├── crud/
│   ├── vocab_crud.py
│   └── score_crud.py
├── database/
│   └── database.py
├── models/
│   ├── vocab.py
│   └── scores.py
├── routers/
│   ├── vocab_router.py
│   └── score_router.py
├── schemas/
│   ├── vocab.py
│   └── scores.py
└── main.py
```

## Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Contact

- Project Owner: [@r00kieAd](https://github.com/r00kieAd)
- Project Link: [https://github.com/r00kieAd/english_vocab_backend](https://github.com/r00kieAd/english_vocab_backend)
