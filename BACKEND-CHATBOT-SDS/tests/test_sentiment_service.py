import importlib
import sys
import types


class FakeSIA:
    def polarity_scores(self, text):
        lower = str(text).lower()
        if "good" in lower:
            return {"pos": 0.8, "neu": 0.2, "neg": 0.0, "compound": 0.8}
        if "bad" in lower:
            return {"pos": 0.0, "neu": 0.2, "neg": 0.8, "compound": -0.8}
        return {"pos": 0.0, "neu": 1.0, "neg": 0.0, "compound": 0.0}


class FakeSentimentIntensityAnalyzer:
    def __call__(self):
        return FakeSIA()


class FakeTextBlob:
    def __init__(self, text):
        lower = str(text).lower()
        if "good" in lower:
            polarity = 0.6
        elif "bad" in lower:
            polarity = -0.6
        else:
            polarity = 0.0
        self.sentiment = types.SimpleNamespace(polarity=polarity, subjectivity=0.5)


def _import_service_module():
    nltk_stub = types.ModuleType("nltk")
    nltk_stub.data = types.SimpleNamespace(find=lambda _: True)
    nltk_stub.download = lambda *args, **kwargs: True

    nltk_sentiment_stub = types.ModuleType("nltk.sentiment")
    nltk_sentiment_stub.SentimentIntensityAnalyzer = FakeSentimentIntensityAnalyzer()

    textblob_stub = types.ModuleType("textblob")
    textblob_stub.TextBlob = FakeTextBlob

    sys.modules["nltk"] = nltk_stub
    sys.modules["nltk.sentiment"] = nltk_sentiment_stub
    sys.modules["textblob"] = textblob_stub

    if "sentimentAnalysisService" in sys.modules:
        del sys.modules["sentimentAnalysisService"]
    return importlib.import_module("sentimentAnalysisService")


def test_parse_llm_response_accepts_code_fences():
    module = _import_service_module()
    service = module.SentimentAnalysisService()
    parsed = service._parse_llm_response('```json {"label":"Positive","confidence":0.9,"language":"English"}```')
    assert parsed["label"] == "Positive"
    assert parsed["confidence"] == 0.9


def test_hybrid_analysis_combines_vader_and_textblob():
    module = _import_service_module()
    service = module.SentimentAnalysisService()
    res = service.analyze_sentiment("good movie", show_details=True, use_hybrid=True)
    assert res["analyzer"].startswith("Hybrid")
    assert res["label"] == "Positive"
    assert "combined_score" in res
    assert "details" in res

