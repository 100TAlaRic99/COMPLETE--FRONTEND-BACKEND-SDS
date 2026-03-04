"""
Sentiment Analysis Service

This module provides sentiment analysis functionality using VADER and TextBlob.
It supports both individual analyzer modes and a hybrid approach for improved accuracy.

Features:
- VADER sentiment analysis (optimized for social media text)
- TextBlob sentiment analysis (better for complex sentences)
- Hybrid approach combining both analyzers
- Detailed analysis with confidence scores and insights
- Comprehensive error handling and fallbacks

Author: AI Assistant
Date: November 2025
"""

import os
import json
import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import logging

# optional OpenAI LLM support (openai >= 1.0.0)
try:
    from openai import OpenAI
    import httpx
except ImportError:
    OpenAI = None
    httpx = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentAnalysisService:
    """
    A comprehensive sentiment analysis service that combines VADER and TextBlob
    for improved accuracy and detailed insights.
    """
    
    def __init__(self):
        """Initialize the sentiment analysis service with required dependencies."""
        self._initialize_nltk()
        self._initialize_textblob()
        self.sia = SentimentIntensityAnalyzer()
        self.openai_client = None
        self.openrouter_client = None
        self._initialize_llm_clients()
        logger.info("SentimentAnalysisService initialized successfully")

    def _initialize_llm_clients(self):
        """Initialize OpenAI and/or OpenRouter clients based on available API keys.

        Priority:
        1. OPENAI_API_KEY -> creates OpenAI client for official endpoint
        2. OPENROUTER_API_KEY -> creates OpenRouter client with custom base_url

        Both clients can coexist, but analyze_sentiment_llm chooses based on
        which key is present (OpenAI takes priority).
        """
        if OpenAI is None:
            logger.warning("OpenAI python package (openai>=1.0.0) not installed; LLM analysis disabled")
            return

        ai_key = os.getenv('OPENAI_API_KEY', '').strip()
        router_key = os.getenv('OPENROUTER_API_KEY', '').strip()

        if ai_key:
            self.openai_client = OpenAI(api_key=ai_key)
            logger.info("OpenAI client initialized for LLM sentiment analysis")

        if router_key:
            router_base_url = os.getenv(
                'OPENROUTER_API_BASE',
                'https://openrouter.ai/api/v1'
            )
            referer = os.getenv('OPENROUTER_SITE_URL', '').strip()
            title = os.getenv('OPENROUTER_APP_NAME', '').strip()
            default_headers = {}
            if referer:
                default_headers['HTTP-Referer'] = referer
            if title:
                default_headers['X-OpenRouter-Title'] = title

            # Create httpx client explicitly to avoid proxy env var issues
            http_client = None
            if httpx is not None:
                try:
                    http_client = httpx.Client()
                except Exception as e:
                    logger.warning(f"Failed to create custom httpx client: {e}")

            client_kwargs = {
                'api_key': router_key,
                'base_url': router_base_url,
            }
            if default_headers:
                client_kwargs['default_headers'] = default_headers
            if http_client:
                client_kwargs['http_client'] = http_client

            self.openrouter_client = OpenAI(**client_kwargs)
            logger.info(
                "OpenRouter client initialized with base_url=%s%s",
                router_base_url,
                " and custom headers" if default_headers else ""
            )

        if not (ai_key or router_key):
            logger.warning("Neither OPENAI_API_KEY nor OPENROUTER_API_KEY set; LLM analysis disabled")
    
    def _initialize_nltk(self):
        """Download and initialize NLTK VADER lexicon if needed."""
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
            logger.info("VADER lexicon already available")
        except LookupError:
            logger.info("Downloading VADER lexicon...")
            nltk.download('vader_lexicon', quiet=True)
            logger.info("VADER lexicon downloaded successfully")
    
    def _initialize_textblob(self):
        """Initialize TextBlob (downloads corpora on first use if needed)."""
        try:
            # TextBlob will automatically download required corpora on first use
            test_blob = TextBlob("test")
            _ = test_blob.sentiment  # Trigger any needed downloads
            logger.info("TextBlob initialized successfully")
        except Exception as e:
            logger.warning(f"TextBlob initialization warning: {e}")
            # TextBlob will still work, just might download on first real use
    
    def analyze_sentiment(self, text, show_details=False, use_hybrid=True, use_llm=False):
        """
        Analyze sentiment using configured analyzers.
        
        Args:
            text (str): Text to analyze
            show_details (bool): Include additional analysis details
            use_hybrid (bool): Use hybrid VADER + TextBlob approach for better accuracy
        
        Returns:
            dict: Sentiment analysis results including label, emoji, scores, and compound score
        
        Note:
            VADER works best with simple, direct sentiment expressions.
            Complex negations or idiomatic expressions may not be accurately classified.
            Hybrid mode combines VADER and TextBlob for improved accuracy.
        """
        try:
            # LLM has highest priority if requested
            if use_llm:
                try:
                    return self.analyze_sentiment_llm(text, show_details)
                except Exception as e:
                    logger.warning(f"LLM analysis failed, using system-prompt fallback: {e}")
                    return self.analyze_sentiment_llm_fallback(text, show_details)

            if use_hybrid:
                return self.analyze_sentiment_hybrid(text, show_details)
            
            # Original VADER-only analysis
            sentiment_scores = self.sia.polarity_scores(str(text))
            compound_score = sentiment_scores['compound']
            
            # Assign sentiment labels
            if compound_score >= 0.05:
                sentiment_label = "Positive"
                emoji = "😊"
            elif compound_score <= -0.05:
                sentiment_label = "Negative"
                emoji = "😡"
            else:
                sentiment_label = "Neutral"
                emoji = "😐"
            
            result = {
                'label': sentiment_label,
                'emoji': emoji,
                'scores': sentiment_scores,
                'compound': compound_score,
                'analyzer': 'VADER'
            }
            
            # Add additional details if requested
            if show_details:
                result['details'] = {
                    'text_length': len(text),
                    'word_count': len(text.split()),
                    'confidence': abs(compound_score),
                    'is_neutral_heavy': sentiment_scores['neu'] > 0.8
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in analyze_sentiment: {e}")
            return self._get_fallback_result(text, str(e))
    
    def analyze_sentiment_hybrid(self, text, show_details=False):
        """
        Hybrid sentiment analysis combining VADER and TextBlob
        
        This approach combines the strengths of both analyzers:
        - VADER: Excellent for social media, emojis, and informal text
        - TextBlob: Better at handling complex sentences and context
        
        Args:
            text (str): Text to analyze
            show_details (bool): Include additional analysis details
        
        Returns:
            dict: Enhanced sentiment analysis results with hybrid scoring
        """
        try:
            text_str = str(text)
            
            # VADER analysis
            vader_scores = self.sia.polarity_scores(text_str)
            vader_compound = vader_scores['compound']
            
            # TextBlob analysis
            try:
                blob = TextBlob(text_str)
                textblob_polarity = blob.sentiment.polarity
                textblob_subjectivity = blob.sentiment.subjectivity
            except Exception as e:
                logger.warning(f"TextBlob analysis failed, using VADER fallback: {e}")
                # Fallback to VADER only if TextBlob fails
                textblob_polarity = vader_compound
                textblob_subjectivity = 0.5
            
            # Weighted combination (VADER 60%, TextBlob 40%)
            # VADER gets more weight as it's optimized for social media/reviews
            combined_score = (vader_compound * 0.6) + (textblob_polarity * 0.4)
            
            # Check if both analyzers agree (within 0.3 threshold)
            agreement = abs(vader_compound - textblob_polarity) < 0.3
            
            # Determine sentiment label with adjusted thresholds
            if combined_score >= 0.05:
                sentiment_label = "Positive"
                emoji = "😊"
            elif combined_score <= -0.05:
                sentiment_label = "Negative"
                emoji = "😡"
            else:
                sentiment_label = "Neutral"
                emoji = "😐"
            
            # Calculate enhanced confidence
            # Higher confidence when both models agree
            base_confidence = abs(combined_score)
            agreement_boost = 0.15 if agreement else 0
            confidence = min(base_confidence + agreement_boost, 1.0)
            
            result = {
                'label': sentiment_label,
                'emoji': emoji,
                'combined_score': round(combined_score, 4),
                'confidence': round(confidence, 4),
                'analyzer': 'Hybrid (VADER + TextBlob)',
                'vader_score': round(vader_compound, 4),
                'textblob_score': round(textblob_polarity, 4),
                'models_agree': agreement,
                'scores': vader_scores  # Keep VADER detailed scores for compatibility
            }
            
            # Add additional details if requested
            if show_details:
                result['details'] = {
                    'text_length': len(text_str),
                    'word_count': len(text_str.split()),
                    'confidence': round(confidence, 4),
                    'is_neutral_heavy': vader_scores['neu'] > 0.8,
                    'subjectivity': round(textblob_subjectivity, 4),
                    'vader_breakdown': {
                        'positive': round(vader_scores['pos'], 4),
                        'negative': round(vader_scores['neg'], 4),
                        'neutral': round(vader_scores['neu'], 4)
                    },
                    'agreement_details': {
                        'models_agree': agreement,
                        'score_difference': round(abs(vader_compound - textblob_polarity), 4),
                        'note': 'Both models agree on sentiment' if agreement else 'Models show different sentiment strengths'
                    }
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in analyze_sentiment_hybrid: {e}")
            return self._get_fallback_result(text, str(e))
    
    def compare_analyzers(self, text, show_details=True, include_llm=False):
        """
        Compare VADER-only vs Hybrid analysis side-by-side
        
        Args:
            text (str): Text to analyze
            show_details (bool): Include detailed breakdown
        
        Returns:
            dict: Comparison results with both analyses and metrics
        """
        try:
            # Get both analyses
            vader_only = self.analyze_sentiment(text, show_details=show_details, use_hybrid=False)
            hybrid = self.analyze_sentiment(text, show_details=show_details, use_hybrid=True)
            
            # Compare results
            same_label = vader_only['label'] == hybrid['label']
            
            comparison = {
                'text': text,
                'vader_only': vader_only,
                'hybrid': hybrid,
                'comparison': {
                    'same_label': same_label,
                    'vader_confidence': vader_only.get('confidence', abs(vader_only.get('compound', 0))),
                    'hybrid_confidence': hybrid['confidence'],
                    'confidence_improvement': round(
                        hybrid['confidence'] - vader_only.get('confidence', abs(vader_only.get('compound', 0))), 
                        4
                    ),
                    'recommendation': 'Hybrid' if hybrid['confidence'] > vader_only.get('confidence', abs(vader_only.get('compound', 0))) else 'VADER'
                }
            }

            if include_llm:
                llm = self.analyze_sentiment(text, show_details=show_details, use_llm=True)
                comparison['llm'] = llm
                comparison['comparison']['llm_confidence'] = llm.get('confidence', 0)
                if llm.get('confidence', 0) > comparison['comparison']['hybrid_confidence']:
                    comparison['comparison']['recommendation'] = 'LLM'

            return comparison
            
        except Exception as e:
            logger.error(f"Error in compare_analyzers: {e}")
            return {'error': str(e), 'text': text}
    
    def generate_insights(self, sentiment_result):
        """
        Generate insights based on sentiment analysis results
        
        Args:
            sentiment_result (dict): Results from sentiment analysis
        
        Returns:
            list: List of insight strings
        """
        insights = []
        
        try:
            details = sentiment_result.get('details', {})
            
            if details.get('is_neutral_heavy'):
                insights.append("⚠️ High neutral content detected. The text may contain complex language or mixed sentiments.")
            
            confidence = details.get('confidence', sentiment_result.get('confidence', 0))
            if confidence < 0.1:
                insights.append("⚠️ Low confidence score. The sentiment is very close to neutral.")
            elif confidence > 0.7:
                insights.append("✓ High confidence score. The sentiment is very clear.")
            
            if details.get('word_count', 0) < 5:
                insights.append("ℹ️ Short text. Longer texts may provide more accurate analysis.")
            
            # Hybrid-specific insights
            if sentiment_result.get('analyzer') == 'Hybrid (VADER + TextBlob)':
                if sentiment_result.get('models_agree'):
                    insights.append("✓ Both VADER and TextBlob agree on the sentiment.")
                else:
                    insights.append("⚠️ VADER and TextBlob show different sentiment strengths.")
                
                subjectivity = details.get('subjectivity', 0)
                if subjectivity > 0.7:
                    insights.append("ℹ️ Highly subjective text detected (opinions, emotions).")
                elif subjectivity < 0.3:
                    insights.append("ℹ️ Objective text detected (facts, neutral statements).")
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            insights.append("⚠️ Unable to generate detailed insights.")
        
        return insights
    
    def _get_fallback_result(self, text, error_msg):
        """
        Generate a fallback result when analysis fails
        
        Args:
            text (str): Original text
            error_msg (str): Error message
        
        Returns:
            dict: Fallback sentiment result
        """
        return {
            'label': 'Neutral',
            'emoji': '😐',
            'scores': {'pos': 0.0, 'neu': 1.0, 'neg': 0.0, 'compound': 0.0},
            'compound': 0.0,
            'analyzer': 'Fallback',
            'error': error_msg,
            'confidence': 0.0
        }

    def analyze_sentiment_llm(self, text, show_details=False, model=None):
        """
        Use an LLM (OpenAI or OpenRouter) to perform multilingual sentiment analysis.

        The model is asked to return a JSON object containing:
        - label: Positive/Negative/Neutral
        - confidence: float 0-1
        - language: detected language (English/Hindi/Marathi/Hinglish/other)

        Provider selection is automatic: if `OPENAI_API_KEY` is set the
        official OpenAI endpoint is used; otherwise if `OPENROUTER_API_KEY`
        exists the request is sent through OpenRouter with model
        `openai/gpt-oss-20b:free` by default.

        Args:
            text (str): Text to analyze
            show_details (bool): If true, request extra detail from the LLM
            model (str): Optional model override (e.g. "gpt-4", "gpt-3.5-turbo",
                         or OpenRouter model identifier)  
        Returns:
            dict: Sentiment result similar to other analyzers.
        """
        # Determine which client to use: prefer OpenAI, fallback to OpenRouter
        client = self.openai_client or self.openrouter_client
        if not client:
            logger.warning("LLM analysis requested but no LLM client configured; falling back to hybrid")
            return self.analyze_sentiment(text, show_details=show_details, use_hybrid=True)

        # Determine which provider is active
        is_openrouter = (self.openai_client is None) and (self.openrouter_client is not None)

        # choose model based on which key/provider is configured
        if not model:
            if is_openrouter:
                # using OpenRouter; allow override via OPENROUTER_MODEL
                model = os.getenv('OPENROUTER_MODEL', 'openai/gpt-oss-20b:free')
            else:
                # using OpenAI; allow override via OPENAI_MODEL
                model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

        provider = "OpenRouter" if is_openrouter else "OpenAI"
        allow_system_prompt = os.getenv('LLM_ALLOW_SYSTEM_PROMPT', 'true').lower() != 'false'

        try:
            return self._invoke_llm_request(
                client=client,
                provider=provider,
                model=model,
                text=text,
                show_details=show_details,
                use_system_prompt=allow_system_prompt
            )
        except Exception as e:
            if allow_system_prompt and self._is_system_prompt_error(e):
                logger.warning(
                    "Provider rejected system prompts (model=%s); retrying with user-only instructions",
                    model
                )
                try:
                    return self._invoke_llm_request(
                        client=client,
                        provider=provider,
                        model=model,
                        text=text,
                        show_details=show_details,
                        use_system_prompt=False
                    )
                except Exception as retry_error:
                    logger.error(f"LLM retry without system prompt failed: {retry_error}")
                    return self._get_fallback_result(text, str(retry_error))

            logger.error(f"Error in analyze_sentiment_llm: {e}")
            return self._get_fallback_result(text, str(e))

    def _invoke_llm_request(self, client, provider, model, text, show_details, use_system_prompt=True):
        logger.info(
            "LLM request sent via %s with model=%s (system_prompt=%s)",
            provider,
            model,
            'enabled' if use_system_prompt else 'disabled'
        )

        messages = self._build_llm_messages(text, show_details, use_system_prompt)

        response_kwargs = {
            'model': model,
            'messages': messages,
            'temperature': 0.0,
        }

        enforce_json = os.getenv('LLM_ENFORCE_JSON', 'true').lower() != 'false'
        if enforce_json:
            response_kwargs['response_format'] = {'type': 'json_object'}

        response = client.chat.completions.create(**response_kwargs)
        content = response.choices[0].message.content or ''

        parsed = self._parse_llm_response(content)

        result = {
            'label': parsed.get('label', 'Neutral'),
            'emoji': '😊' if parsed.get('label', '').lower().startswith('pos') else ('😡' if parsed.get('label', '').lower().startswith('neg') else '😐'),
            'confidence': parsed.get('confidence', 0),
            'language': parsed.get('language', 'unknown'),
            'analyzer': f'LLM ({provider} / {model})',
            'provider': provider,
            'model': model,
            'raw': parsed,
        }
        if show_details and 'reason' in parsed:
            result['details'] = {'reason': parsed['reason']}
        return result

    def _build_llm_messages(self, text, show_details, use_system_prompt=True):
        """Create chat messages that force the model to emit raw JSON only."""
        detail_clause = (
            "Include a concise 'reason' field explaining the sentiment." if show_details else "Do not include a 'reason' field unless it is necessary."
        )
        system_prompt = (
            "You are a strict sentiment analysis engine. "
            "Always respond with a single JSON object and NOTHING else. "
            "Never wrap the JSON in code fences, markdown, prose, or commentary."
        )
        schema_prompt = (
            "Output JSON with keys: label (Positive/Negative/Neutral), confidence (number 0-1), "
            "language (English/Hindi/Marathi/Hinglish/Other). "
            f"{detail_clause}"
        )
        user_prompt = (
            f"Text to analyze: {str(text)}"
        )

        if use_system_prompt:
            return [
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": schema_prompt},
                {"role": "user", "content": user_prompt},
            ]

        combined_prompt = (
            f"{system_prompt} {schema_prompt}\n{user_prompt}"
        )
        return [{"role": "user", "content": combined_prompt}]

    def _parse_llm_response(self, content):
        """Strip any formatting and parse JSON content from the LLM response."""
        cleaned = content.strip()

        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r"```$", "", cleaned).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass

        logger.warning("Failed to parse JSON from LLM: %s", content)
        raise ValueError("LLM response was not valid JSON")

    @staticmethod
    def _is_system_prompt_error(error):
        message = str(error).lower()
        return (
            'developer instruction is not enabled' in message
            or 'system instruction is not enabled' in message
        )
    
    def get_test_samples(self):
        """
        Get predefined test samples for sentiment analysis validation
        
        Returns:
            list: List of test samples with expected results
        """
        return [
            {
                'id': 1,
                'text': "This movie doesn't scrape the bottom of the barrel. This movie isn't the bottom of the barrel. This movie isn't below the bottom of the barrel. This movie doesn't deserve to be mentioned in the same sentence with barrels.",
                'expected': 'Negative',
                'note': 'Complex negations - VADER may struggle with this'
            },
            {
                'id': 2,
                'text': "This movie is terrible, awful, and horrible. I hated every minute of it.",
                'expected': 'Negative',
                'note': 'Simple negative words - VADER handles this well'
            },
            {
                'id': 3,
                'text': "This movie is amazing! Best film I've ever seen. Absolutely loved it!",
                'expected': 'Positive',
                'note': 'Simple positive words - VADER handles this well'
            },
            {
                'id': 4,
                'text': "The movie was okay. Nothing special but not bad either.",
                'expected': 'Neutral',
                'note': 'Mixed sentiment - may lean positive'
            },
            {
                'id': 5,
                'text': "Worst movie ever! Complete waste of time and money.",
                'expected': 'Negative',
                'note': 'Clear negative sentiment'
            },
            {
                'id': 6,
                'text': "I absolutely hated this film. Boring, terrible acting, awful plot.",
                'expected': 'Negative',
                'note': 'Strong negative sentiment'
            },
            # multilingual examples for LLM evaluation
            {
                'id': 7,
                'text': "यह फिल्म बहुत अच्छी थी, मुझे बहुत पसंद आई।",
                'expected': 'Positive',
                'note': 'Hindi positive review'
            },
            {
                'id': 8,
                'text': "फिल्म बेकार थी, बिलकुल भी मज़ा नहीं आया।",
                'expected': 'Negative',
                'note': 'Hindi negative review'
            },
            {
                'id': 9,
                'text': "अभिनय चांगला नव्हता, पण कथा ठीक होती.",
                'expected': 'Negative',
                'note': 'Marathi mixed sentiment'
            },
            {
                'id': 10,
                'text': "movie mast hoti yaar, full paisa vasool!",
                'expected': 'Positive',
                'note': 'Hinglish praising the film'
            }
        ]
    
    def test_samples_analysis(self):
        """
        Run analysis on test samples and return results with accuracy metrics
        
        Returns:
            dict: Test results with accuracy statistics
        """
        test_reviews = self.get_test_samples()
        results = []
        
        for review in test_reviews:
            sentiment = self.analyze_sentiment(review['text'], show_details=True)
            results.append({
                'id': review['id'],
                'text': review['text'],
                'expected': review['expected'],
                'actual': sentiment['label'],
                'correct': sentiment['label'] == review['expected'],
                'sentiment': sentiment,
                'note': review['note']
            })
        
        # Calculate accuracy
        correct_count = sum(1 for r in results if r['correct'])
        accuracy = (correct_count / len(results)) * 100
        
        return {
            'results': results,
            'summary': {
                'total': len(results),
                'correct': correct_count,
                'accuracy': f"{accuracy:.1f}%"
            },
            'info': {
                'analyzer': 'Hybrid (VADER + TextBlob)',
                'description': 'Combines VADER (60%) and TextBlob (40%) for improved accuracy',
                'best_for': 'Social media text, reviews, and complex sentences',
                'improvements': 'Better handling of context and complex language patterns'
            }
        }


# Create a singleton instance for easy importing
sentiment_service = SentimentAnalysisService()

# Convenience functions for backward compatibility
def analyze_sentiment(text, show_details=False, use_hybrid=True):
    """Convenience function that uses the singleton service instance"""
    return sentiment_service.analyze_sentiment(text, show_details, use_hybrid)

def analyze_sentiment_hybrid(text, show_details=False):
    """Convenience function that uses the singleton service instance"""
    return sentiment_service.analyze_sentiment_hybrid(text, show_details)
