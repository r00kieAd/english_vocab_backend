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

### Server Endpoints

- `GET /` - Server health check and status

### Vocabulary Endpoints

- `GET /vocabs/` - Get vocabulary endpoints information
- `GET /vocabs/read` - Get all vocabulary entries
- `GET /vocabs/read/vocab_types` - Get all the word types
- `GET /vocabs/read/count/{word_type}` - Get the count of specific word type
- `GET /vocabs/read/{word_type}?{word_count}` - Get all the words of a specific word type, limit optional
- `POST /vocabs/create` - Create a new vocabulary entry
- `PUT /vocabs/update/{word}` - Update an existing vocabulary entry

Example vocabulary response:
```json
{
    "word": "ardent",
    "word_type": "adjective",
    "meaning": "Very passionate or enthusiastic",
    "example": "He is an ardent supporter of environmental causes."
}
```

### Score Endpoints

- `GET /scores/` - Get score endpoints information
- `GET /scores/all_scores` - Get all scores (leaderboard)
- `GET /scores/high_score` - Get the highest score
- `POST /scores/insert_score` - Insert a new score entry

Example score response:
```json
{
    "high_score": 100,
    "high_scorer": "Player1"
}
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
