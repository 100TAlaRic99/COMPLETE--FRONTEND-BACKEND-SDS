import importlib
import sys
import types
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
from bson.objectid import ObjectId


class FakeSentimentService:
    def analyze_sentiment(self, text, show_details=False, use_hybrid=True, use_llm=False):
        return {
            "label": "Positive" if "good" in str(text).lower() else "Neutral",
            "emoji": "😊" if "good" in str(text).lower() else "😐",
            "scores": {"pos": 0.9, "neu": 0.1, "neg": 0.0, "compound": 0.9},
            "compound": 0.9,
            "analyzer": "Fake",
        }

    def test_samples_analysis(self):
        return {"results": [], "summary": {"total": 0, "correct": 0, "accuracy": "0.0%"}}

    def generate_insights(self, sentiment_result):
        return []

    def compare_analyzers(self, text, show_details=True, include_llm=False):
        return {"text": text, "vader_only": {}, "hybrid": {}, "comparison": {}}


@dataclass
class FakeInsertResult:
    inserted_id: ObjectId


@dataclass
class FakeDeleteResult:
    deleted_count: int


class FakeCursor:
    def __init__(self, items):
        self._items = list(items)

    def sort(self, key, direction):
        reverse = direction == -1
        self._items.sort(key=lambda x: x.get(key), reverse=reverse)
        return self

    def skip(self, n):
        self._items = self._items[n:]
        return self

    def limit(self, n):
        self._items = self._items[:n]
        return self

    def __iter__(self):
        return iter(self._items)


class FakeCollection:
    def __init__(self):
        self._items = []

    def find_one(self, query):
        for item in self._items:
            ok = True
            for k, v in query.items():
                if item.get(k) != v:
                    ok = False
                    break
            if ok:
                return dict(item)
        return None

    def insert_one(self, doc):
        stored = dict(doc)
        stored["_id"] = stored.get("_id", ObjectId())
        self._items.append(stored)
        return FakeInsertResult(inserted_id=stored["_id"])

    def delete_one(self, query):
        for i, item in enumerate(self._items):
            ok = True
            for k, v in query.items():
                if item.get(k) != v:
                    ok = False
                    break
            if ok:
                del self._items[i]
                return FakeDeleteResult(deleted_count=1)
        return FakeDeleteResult(deleted_count=0)

    def find(self, query):
        results = []
        for item in self._items:
            ok = True
            for k, v in query.items():
                if item.get(k) != v:
                    ok = False
                    break
            if ok:
                results.append(dict(item))
        return FakeCursor(results)

    def count_documents(self, query):
        return sum(1 for _ in self.find(query))


class DummyBcrypt:
    def generate_password_hash(self, password):
        return f"hashed::{password}".encode("utf-8")

    def check_password_hash(self, hashed, password):
        return str(hashed) == f"hashed::{password}"


@pytest.fixture()
def app_module(monkeypatch):
    stub = types.ModuleType("sentimentAnalysisService")
    stub.sentiment_service = FakeSentimentService()
    sys.modules["sentimentAnalysisService"] = stub

    if "app" in sys.modules:
        del sys.modules["app"]
    module = importlib.import_module("app")

    module.users_collection = FakeCollection()
    module.chats_collection = FakeCollection()
    module.bcrypt = DummyBcrypt()

    return module


@pytest.fixture()
def client(app_module):
    return app_module.app.test_client()


@pytest.fixture()
def auth_header(app_module):
    with app_module.app.app_context():
        token = app_module.create_access_token(identity="user-1")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def now_utc():
    return datetime.now(timezone.utc)

