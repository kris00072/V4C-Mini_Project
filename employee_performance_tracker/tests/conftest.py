import os
import sys
import tempfile
import types
import pytest

# Ensure project root (one level up from tests/) is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import after path adjustment
from database_connections import get_sqlite_connection, init_sqlite_db


@pytest.fixture()
def temp_sqlite_db(monkeypatch):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        # Patch environment for SQLite file
        conn = get_sqlite_connection(path)
        init_sqlite_db(conn)
        yield conn
    finally:
        try:
            conn.close()
        except Exception:
            pass
        try:
            os.remove(path)
        except Exception:
            pass


class FakeDatabase:
    def __init__(self):
        self._store = {"counters": FakeCounters()}

    def __getitem__(self, key):
        return self._store[key]


class FakeMongoCollection:
    def __init__(self):
        self._docs = []
        self.database = FakeDatabase()

    def insert_one(self, doc):
        # mimic ObjectId with simple str counter
        doc = dict(doc)
        oid = f"oid_{len(self._docs)+1}"
        doc.setdefault("_id", oid)
        self._docs.append(doc)
        return types.SimpleNamespace(inserted_id=oid)

    def find(self, query=None, projection=None):
        query = query or {}
        def match(d):
            for k, v in query.items():
                if isinstance(v, dict) and "$exists" in v:
                    exists = v["$exists"]
                    if (k in d) != (bool(exists)):
                        return False
                elif isinstance(v, dict) and "$regex" in v:
                    needle = str(v["$regex"]).lower()
                    hay = str(d.get(k, "")).lower()
                    if needle not in hay:
                        return False
                elif isinstance(v, dict) and ("$gte" in v or "$lte" in v):
                    val = d.get(k)
                    if val is None:
                        return False
                    if "$gte" in v and not (val >= v["$gte"]):
                        return False
                    if "$lte" in v and not (val <= v["$lte"]):
                        return False
                else:
                    if d.get(k) != v:
                        return False
            return True
        return FakeCursor([d for d in self._docs if match(d)])

    def find_one(self, selector):
        for d in self._docs:
            ok = all(d.get(k) == v for k, v in selector.items())
            if ok:
                return d
        return None

    def update_one(self, selector, update):
        for d in self._docs:
            ok = all(d.get(k) == v for k, v in selector.items())
            if ok:
                if "$set" in update:
                    d.update(update["$set"])
                if "$max" in update:
                    for k, v in update["$max"].items():
                        if d.get(k, float("-inf")) < v:
                            d[k] = v
                return types.SimpleNamespace(modified_count=1)
        return types.SimpleNamespace(modified_count=0)

    def delete_one(self, selector):
        for i, d in enumerate(self._docs):
            ok = all(d.get(k) == v for k, v in selector.items())
            if ok:
                del self._docs[i]
                return types.SimpleNamespace(deleted_count=1)
        return types.SimpleNamespace(deleted_count=0)

    def aggregate(self, pipeline):
        # Support two patterns:
        # 1) [{"$group": {"_id": None, "maxId": {"$max": "$review_id"}}}]
        # 2) [{"$match": {"employee_id": X}}, {"$group": {"_id": None, "average_rating": {"$avg": "$overall_rating"}, "review_count": {"$sum": 1}}}]
        if not pipeline:
            return iter([])
        docs = list(self._docs)
        # $match stage
        if "$match" in pipeline[0]:
            match = pipeline[0]["$match"]
            filtered = []
            for d in docs:
                ok = True
                for k, v in match.items():
                    if d.get(k) != v:
                        ok = False
                        break
                if ok:
                    filtered.append(d)
            docs = filtered
            group_stage = pipeline[1]["$group"] if len(pipeline) > 1 and "$group" in pipeline[1] else {}
        else:
            group_stage = pipeline[0]["$group"] if "$group" in pipeline[0] else {}

        if group_stage:
            result = {"_id": group_stage.get("_id")}
            if "maxId" in group_stage:
                max_id = None
                for d in docs:
                    rid = d.get("review_id")
                    if rid is not None:
                        max_id = rid if max_id is None else max(max_id, rid)
                if max_id is not None:
                    result["maxId"] = max_id
                else:
                    return iter([])
            if "average_rating" in group_stage or "review_count" in group_stage:
                ratings = [float(d.get("overall_rating", 0)) for d in docs if d.get("overall_rating") is not None]
                count = len(ratings)
                avg = sum(ratings) / count if count else None
                result["average_rating"] = avg
                result["review_count"] = count
            return iter([result])
        return iter([])


class FakeCursor:
    def __init__(self, docs):
        self._docs = list(docs)

    def sort(self, key, order=None):
        if isinstance(key, list):
            fields = key
        else:
            fields = [(key, order or -1)]
        for k, direction in reversed(fields):
            self._docs.sort(key=lambda d: d.get(k), reverse=(direction == -1))
        return self

    def limit(self, n):
        self._docs = self._docs[:n]
        return self

    def __iter__(self):
        return iter(self._docs)


class FakeCounters:
    def __init__(self):
        self._seqs = {"review_id": {"_id": "review_id", "seq": 0}}

    def find_one_and_update(self, selector, update, upsert=False, return_document=None):
        doc = self._seqs.setdefault(selector["_id"], {"_id": selector["_id"], "seq": 0})
        if "$inc" in update:
            for k, v in update["$inc"].items():
                doc[k] = doc.get(k, 0) + v
        return doc

    def update_one(self, selector, update, upsert=False):
        doc = self._seqs.setdefault(selector["_id"], {"_id": selector["_id"], "seq": 0})
        if "$max" in update:
            for k, v in update["$max"].items():
                doc[k] = max(doc.get(k, 0), v)
        self._seqs[selector["_id"]] = doc
        return types.SimpleNamespace(modified_count=1)


@pytest.fixture()
def fake_mongo_collection():
    return FakeMongoCollection()


