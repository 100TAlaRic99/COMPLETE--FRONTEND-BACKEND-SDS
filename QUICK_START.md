# Quick Start Guide - New Features

## 🚀 Testing the Improvements

### 1. Start the Server

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python app.py
```

You should see cleaner logs now (no verbose NLTK messages) ✓

---

## 🧪 Test Sample Reviews (No Authentication Required)

### Using curl:
```bash
curl http://localhost:5000/api/test-samples | jq
```

### Using Python:
```python
import requests
response = requests.get('http://localhost:5000/api/test-samples')
print(response.json())
```

### Using Browser:
Navigate to: `http://localhost:5000/api/test-samples`

### What You'll See:
- 6 test reviews with expected vs. actual sentiment
- Accuracy metrics
- Notes on VADER's performance
- Information about limitations

---

## 🔍 Enhanced Analysis (Requires Authentication)

### Step 1: Get a JWT Token

**Register:**
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Or Login:**
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

Save the `access_token` from the response.

### Step 2: Use Detailed Analysis

```bash
# Replace YOUR_TOKEN with the actual token
curl -X POST http://localhost:5000/api/analyze-detailed \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This movie is absolutely amazing! Best film ever!",
    "save_to_history": true
  }'
```

### What You'll Get:
```json
{
  "text": "This movie is absolutely amazing! Best film ever!",
  "sentiment": {
    "label": "Positive",
    "emoji": "😊",
    "scores": {
      "pos": 0.655,
      "neu": 0.345,
      "neg": 0.0,
      "compound": 0.8834
    },
    "compound": 0.8834,
    "details": {
      "text_length": 48,
      "word_count": 8,
      "confidence": 0.8834,
      "is_neutral_heavy": false
    },
    "insights": [
      "✓ High confidence score. The sentiment is very clear."
    ]
  }
}
```

---

## 🎯 Try Different Examples

### Positive Example:
```bash
curl -X POST http://localhost:5000/api/analyze-detailed \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this! Absolutely fantastic and wonderful!"}'
```

### Negative Example:
```bash
curl -X POST http://localhost:5000/api/analyze-detailed \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "This is terrible, awful, and horrible. I hate it!"}'
```

### Neutral Example:
```bash
curl -X POST http://localhost:5000/api/analyze-detailed \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "The product arrived on time. It works as described."}'
```

### Complex Negation (VADER struggles):
```bash
curl -X POST http://localhost:5000/api/analyze-detailed \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "This movie doesn'\''t scrape the bottom of the barrel."}'
```

---

## 🧪 Run the Test Script

We've included a Python test script:

```bash
# Install colorama for pretty output (optional)
pip install colorama

# Run the test script
python test_improvements.py
```

This will:
- ✓ Check if server is running
- ✓ Test the samples endpoint
- ✓ Show example usage for detailed analysis

---

## 📊 Understanding the Results

### Sentiment Scores Explained:

| Score | Range | Meaning |
|-------|-------|---------|
| **Positive** | 0.0 - 1.0 | Proportion of positive words |
| **Neutral** | 0.0 - 1.0 | Proportion of neutral words |
| **Negative** | 0.0 - 1.0 | Proportion of negative words |
| **Compound** | -1.0 to +1.0 | Overall sentiment score |

### Compound Score Interpretation:
- **≥ 0.05**: Positive 😊
- **-0.05 to 0.05**: Neutral 😐
- **≤ -0.05**: Negative 😡

### Insights You Might See:

| Insight | Meaning |
|---------|---------|
| ⚠️ High neutral content | Text has >80% neutral words, may be complex |
| ⚠️ Low confidence | Compound score < 0.1, sentiment unclear |
| ✓ High confidence | Compound score > 0.7, sentiment very clear |
| ℹ️ Short text | Less than 5 words, may need more context |

---

## 🎓 Best Practices

### ✅ DO:
- Use simple, direct language
- Include clear sentiment words (love, hate, great, terrible)
- Use exclamation marks for emphasis
- Write longer texts (5+ words) for better accuracy

### ❌ DON'T:
- Use complex double/triple negations
- Rely on sarcasm or irony
- Use only neutral words
- Expect perfect accuracy with idioms

---

## 🔄 Comparing Endpoints

### Standard `/api/analyze`:
```json
{
  "text": "Great movie!",
  "sentiment": {
    "label": "Positive",
    "emoji": "😊",
    "scores": {...},
    "compound": 0.6588
  }
}
```

### Enhanced `/api/analyze-detailed`:
```json
{
  "text": "Great movie!",
  "sentiment": {
    "label": "Positive",
    "emoji": "😊",
    "scores": {...},
    "compound": 0.6588,
    "details": {
      "text_length": 12,
      "word_count": 2,
      "confidence": 0.6588,
      "is_neutral_heavy": false
    },
    "insights": [
      "✓ High confidence score. The sentiment is very clear.",
      "ℹ️ Short text. Longer texts may provide more accurate analysis."
    ]
  }
}
```

**Use detailed endpoint when:**
- You need confidence scores
- You want automatic insights
- You're building a production app
- You need to explain results to users

---

## 📱 Frontend Integration (Coming Soon)

The frontend can be updated to use the new detailed endpoint:

```javascript
// In Chat.js
const handleSubmitDetailed = async (e) => {
  e.preventDefault();
  
  const response = await axios.post(
    '/api/analyze-detailed',
    { text: inputText, save_to_history: true },
    getAuthHeaders()
  );
  
  // Now you have access to insights and details
  const { sentiment } = response.data;
  console.log('Insights:', sentiment.insights);
  console.log('Confidence:', sentiment.details.confidence);
};
```

---

## 🐛 Troubleshooting

### Server won't start:
```bash
# Check if MongoDB is running
mongod --version

# Check if port 5000 is available
lsof -i :5000

# Activate virtual environment
source venv/bin/activate
```

### Can't access endpoints:
```bash
# Check server is running
curl http://localhost:5000/api/health

# Check your JWT token is valid
# Tokens expire after 24 hours
```

### NLTK errors:
```bash
# Manually download VADER lexicon
python -c "import nltk; nltk.download('vader_lexicon')"
```

---

## 📚 Next Steps

1. ✓ Test the new endpoints
2. ✓ Read `SENTIMENT_IMPROVEMENTS.md` for details
3. ✓ Check `CHANGELOG.md` for version history
4. ✓ Explore the code in `backend/app.py`
5. ✓ Consider integrating detailed analysis in frontend

---

## 💡 Tips

- **For demos**: Use `/api/test-samples` to show VADER's capabilities
- **For production**: Use `/api/analyze-detailed` for better user experience
- **For learning**: Read the insights to understand VADER's behavior
- **For debugging**: Check the confidence scores and neutral content warnings

---

## 🎉 You're Ready!

Start experimenting with the new features. The improvements make sentiment analysis more transparent and user-friendly while maintaining backward compatibility.

Happy analyzing! 🚀
