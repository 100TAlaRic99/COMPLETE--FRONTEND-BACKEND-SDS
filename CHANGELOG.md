# Changelog

All notable changes to this project will be documented in this file.

## [v1.2.0] - 2025-02-28

### Added
- 🤖 **LLM Sentiment Engine**: optional OpenAI GPT-based analyzer supporting English, Hindi, Marathi and Hinglish
  - Configurable via `OPENAI_API_KEY` and `OPENAI_MODEL`
  - Accessible through new `analyzer` parameter on `/api/analyze` and `/api/analyze-detailed`
  - Included in comparison endpoint with `include_llm=true`
  - Lighthouse test added to `test_refactored_service.py`

### Changed
- Backend logic remains intact; LLM is an additive layer preserving VADER/TextBlob behavior
- Frontend UI option to choose analyzer
- Updated documentation and requirements

## [v1.1.0] - 2024-11-08

### Added
- 🔇 **Quiet NLTK Download**: Suppressed verbose NLTK download messages for cleaner logs
- 📊 **Enhanced Sentiment Analysis**: Added `show_details` parameter to `analyze_sentiment()` function
  - Text length and word count
  - Confidence score calculation
  - Neutral-heavy content detection
- 🧪 **Test Samples Endpoint** (`/api/test-samples`): New public endpoint to demonstrate VADER capabilities
  - 6 predefined test reviews
  - Expected vs. actual sentiment comparison
  - Accuracy metrics
  - Performance notes for each sample
- 🔍 **Detailed Analysis Endpoint** (`/api/analyze-detailed`): Enhanced analysis with smart insights
  - All standard sentiment scores
  - Additional metadata (text length, word count, confidence)
  - Automatic insights generation:
    - High neutral content warning
    - Low/high confidence notifications
    - Short text notices
  - Optional history saving
- 📖 **Comprehensive Documentation**: Added `SENTIMENT_IMPROVEMENTS.md` with detailed explanations
- 🧪 **Test Script**: Added `test_improvements.py` for easy verification of new features

### Changed
- Updated `analyze_sentiment()` function with better documentation
- Enhanced README.md with new features and endpoints
- Improved code comments and docstrings

### Documentation
- Added detailed VADER limitations explanation
- Included best practices for users and developers
- Added API usage examples with curl commands
- Documented performance metrics and accuracy

### Technical Details
- No breaking changes - fully backward compatible
- No new dependencies required
- No database schema changes
- All improvements use existing NLTK VADER

---

## [v1.0.0] - Initial Release

### Features
- User authentication with JWT
- Real-time sentiment analysis using VADER
- Chat history storage in MongoDB
- Modern React frontend
- RESTful API backend with Flask
- Secure password hashing with Bcrypt

### Endpoints
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `GET /api/user` - Get user info
- `POST /api/analyze` - Analyze sentiment
- `GET /api/history` - Get chat history
- `DELETE /api/history/<chat_id>` - Delete chat entry
- `GET /api/health` - Health check

---

## Future Roadmap

### Planned Features
- [ ] Batch text analysis
- [ ] Sentiment trend visualization
- [ ] Export chat history (CSV/PDF)
- [ ] Multi-language support
- [ ] Dark mode theme
- [ ] User profile management
- [ ] Real-time collaboration

### Potential Enhancements
- [ ] Preprocessing layer for complex negations
- [ ] Transformer-based models (BERT, RoBERTa)
- [ ] Ensemble methods combining multiple analyzers
- [ ] Custom lexicon for domain-specific terms
- [ ] Sarcasm detection
- [ ] Emotion classification (beyond positive/negative/neutral)

---

## Migration Guide

### From v1.0.0 to v1.1.0

**No migration required!** All changes are backward compatible.

**To use new features:**

1. **Test Samples Endpoint** (no auth required):
   ```bash
   curl http://localhost:5000/api/test-samples
   ```

2. **Detailed Analysis** (requires JWT):
   ```bash
   curl -X POST http://localhost:5000/api/analyze-detailed \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"text": "Your text here"}'
   ```

3. **Run Test Script**:
   ```bash
   python test_improvements.py
   ```

**Optional Updates:**
- Review `SENTIMENT_IMPROVEMENTS.md` for best practices
- Consider using `/api/analyze-detailed` instead of `/api/analyze` for richer insights
- Use `/api/test-samples` to educate users about VADER's capabilities

---

## Contributors

- Development Team
- Sentiment Analysis Research

---

## License

Educational purposes only.
