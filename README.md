# Sentiment Analysis Chatbot

A full-stack web application that analyzes the sentiment of text input using NLTK's VADER (Valence Aware Dictionary and sEntiment Reasoner) sentiment analysis tool. The application features user authentication, real-time sentiment analysis, and chat history storage.

## Features

- 🔐 **User Authentication**: Secure registration and login with JWT tokens
- 💬 **Real-time Sentiment Analysis**: Analyze text sentiment instantly using VADER
- 📊 **Detailed Sentiment Scores**: View positive, negative, neutral, and compound scores
- 🔍 **Enhanced Analysis**: NEW! Get insights and confidence scores with detailed endpoint
- 🧪 **Test Samples**: NEW! Test VADER's capabilities with predefined examples
- 📝 **Chat History**: Store and view previous sentiment analyses
- 🎨 **Modern UI**: Beautiful, responsive interface built with React
- 🗄️ **MongoDB Integration**: Persistent storage for users and chat data

## Tech Stack

### Backend
- **Flask**: Python web framework
- **MongoDB**: NoSQL database for data storage
- **NLTK VADER**: Sentiment analysis engine
- **TextBlob**: Supplementary sentiment analysis for hybrid mode
- **OpenAI GPT (LLM)**: Optional multilingual sentiment engine (English, Hindi, Marathi, Hinglish)
- **JWT**: Secure authentication
- **Flask-CORS**: Cross-origin resource sharing
- **Bcrypt**: Password hashing

### Frontend
- **React**: UI library
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **Lucide React**: Modern icon library
- **CSS3**: Custom styling with gradients and animations

## Prerequisites

- Python 3.8+
- Node.js 14+
- MongoDB (local or cloud instance)
- npm or yarn

## Deployment

For step-by-step instructions on how to deploy this application to production (MongoDB Atlas, Render, Vercel), please refer to [DEPLOYMENT.md](./DEPLOYMENT.md).

## Installation

### 1. Clone the Repository

```bash
cd /path/to/finalprojectv2
```

### 2. Backend Setup

> ⚠️ **Optional LLM Setup:** After copying `.env.example` to `.env`, set `OPENAI_API_KEY` (or `OPENROUTER_API_KEY`).
> OpenAI has priority; if no OpenAI key is provided but an OpenRouter key
> exists, the app will route LLM calls through OpenRouter using the model
> `openai/gpt-oss-20b:free` by default. You can override models with
> `OPENAI_MODEL` or `OPENROUTER_MODEL` respectively.

```bash
# Navigate to backend directory
cd backend

# Create virtual environment :PS : note : this step needs to be done only once while initialisng the app .. !!
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env file with your MongoDB URI, JWT secret, and optional LLM keys
# MONGO_URI=mongodb://localhost:27017/sentiment_app
# JWT_SECRET_KEY=your-secret-key-here
# OPENAI_API_KEY=sk-...       # first preference
# OPENAI_MODEL=gpt-4
# OPENROUTER_API_KEY=sk-...   # used only if OPENAI_API_KEY not set
# OPENROUTER_MODEL=openai/gpt-oss-20b:free
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

### 4. MongoDB Setup

Make sure MongoDB is running:

```bash
# If using local MongoDB
mongod

# Or use MongoDB Atlas (cloud) and update MONGO_URI in .env
```

## Running the Application

### Start Backend Server

```bash
# From backend directory with venv activated
python app.py
```

The backend will run on `http://localhost:5000`

### Start Frontend Development Server

```bash
# From frontend directory
npm start
```

The frontend will run on `http://localhost:3000`

## Usage

1. **Register**: Create a new account with username, email, and password
2. **Login**: Sign in with your credentials
3. **Analyze Sentiment**: Type any text in the input box and click send
4. **View Results**: See the sentiment label (Positive/Negative/Neutral) with detailed scores
5. **Check History**: Click the history icon to view past analyses
6. **Logout**: Click the logout button when done

## API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - Login user
- `GET /api/user` - Get current user info (requires JWT)

### Sentiment Analysis
- `POST /api/analyze` - Analyze text sentiment (requires JWT). Body may include `analyzer` field: `vader`, `hybrid` (default) or `llm`.
- `POST /api/analyze-detailed` - **NEW!** Enhanced analysis with insights (requires JWT). Supports the same `analyzer` options.
- `POST /api/compare-analyzers` - Compare VADER vs Hybrid; set `include_llm=true` in body to include LLM results.
- `GET /api/test-samples` - **NEW!** Test VADER with sample reviews (no auth required)
- `GET /api/history` - Get user's chat history (requires JWT)
- `DELETE /api/history/<chat_id>` - Delete a chat entry (requires JWT)

### Health Check
- `GET /api/health` - Check server status

> 📖 **See [SENTIMENT_IMPROVEMENTS.md](./SENTIMENT_IMPROVEMENTS.md) for detailed documentation on new features and enhancements.**

## Sentiment Analysis

The application uses NLTK's VADER sentiment analyzer which provides:

- **Compound Score**: Overall sentiment (-1 to +1)
  - ≥ 0.05: Positive 😊
  - ≤ -0.05: Negative 😡
  - Between: Neutral 😐
- **Positive Score**: Proportion of positive sentiment
- **Negative Score**: Proportion of negative sentiment
- **Neutral Score**: Proportion of neutral sentiment

## Project Structure

```
finalprojectv2/
├── backend/
│   ├── app.py              # Flask application
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variables template
│   └── .gitignore
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.js
│   │   │   ├── Register.js
│   │   │   ├── Chat.js
│   │   │   ├── Auth.css
│   │   │   └── Chat.css
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── index.js
│   │   └── index.css
│   ├── package.json
│   └── .gitignore
└── README.md
```

## Security Features

- Password hashing with Bcrypt
- JWT token-based authentication
- Protected API routes
- CORS configuration
- Environment variable management

## Future Enhancements

- [ ] Export chat history to CSV/PDF
- [ ] Sentiment trend visualization
- [ ] Multi-language support
- [ ] Batch text analysis
- [ ] User profile management
- [ ] Dark mode theme
- [ ] Real-time collaboration

## Troubleshooting

### MongoDB Connection Issues
- Ensure MongoDB is running
- Check MONGO_URI in .env file
- Verify network connectivity for cloud MongoDB

### NLTK Data Issues
- The app automatically downloads VADER lexicon on first run
- If issues persist, manually download: `python -c "import nltk; nltk.download('vader_lexicon')"`

### Port Conflicts
- Backend default: 5000 (change in app.py)
- Frontend default: 3000 (change in package.json)

## License

This project is created for educational purposes.

## Contributors

- Your Name

## Acknowledgments

- NLTK VADER for sentiment analysis
- Flask and React communities
- MongoDB documentation
