"""
Disk cache of query-time embeddings for the ranking experiments, so that a rerun is free and gives the same vectors.
The search UI itself never caches. Every new call is counted with its characters, for the spending ledger.

    embedder = CachedEmbedder(common.QueryEmbedder(model, dim), DATA / "embeddings.sqlite")
"""
import hashlib
import sqlite3
import threading

import numpy as np

USD_PER_TOKEN = 0.20 / 1_000_000  # text input of the embedding model (feature_extraction/config/extraction.yaml); 4 characters count as one token


class CachedEmbedder:
    def __init__(self, embedder, path):
        self.embedder, self.lock = embedder, threading.Lock()
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.execute("create table if not exists vectors (key text primary key, text text, vector blob)")
        self.db.execute("create table if not exists calls (at text default current_timestamp, chars integer)")
        self.calls = self.hits = self.chars = 0

    def key(self, text):
        return hashlib.sha256(f"{self.embedder.model}|{self.embedder.dim}|{text}".encode()).hexdigest()

    def __call__(self, text):
        key = self.key(text)
        with self.lock:
            row = self.db.execute("select vector from vectors where key = ?", (key,)).fetchone()
        if row:
            self.hits += 1
            return np.frombuffer(row[0], np.float32).copy()
        vector = np.asarray(self.embedder(text), np.float32)
        with self.lock:
            self.db.execute("insert or replace into vectors values (?, ?, ?)", (key, text, vector.tobytes()))
            self.db.execute("insert into calls (chars) values (?)", (len(text),))
            self.db.commit()
            self.calls += 1
            self.chars += len(text)
        return vector

    def known(self, text):
        with self.lock:
            return self.db.execute("select 1 from vectors where key = ?", (self.key(text),)).fetchone() is not None

    def spent(self):
        """-> (calls, estimated dollars) of every call ever made through this cache file."""
        with self.lock:
            n, chars = self.db.execute("select count(*), coalesce(sum(chars), 0) from calls").fetchone()
        return n, chars / 4 * USD_PER_TOKEN
