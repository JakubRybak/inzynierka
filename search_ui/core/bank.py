"""
Phrase-bank ranking: residual phrases seen before carry labels made offline by Gemini (ranking_data/phrase_bank.jsonl):
their kind, negation, an English version and the concepts they ask for. Every residual phrase is embedded with the
same model as the products (Gemini Embedding 2):
- a phrase found in the bank takes its labels;
- another phrase takes the labels of its nearest bank phrase when the similarity is at least NEAREST;
- otherwise it takes the concept whose name is the most similar, when that similarity is at least CONCEPT_MATCH.
A lightness word right before a colour in the query ("light" in "light pink dress", which a parser may split
from the colour) is read as a shade, whatever the bank says about it alone ("light" there means lightweight). With the
product colours (colours.py), a shade phrase gets a target colour: its bank hex, a colour name of the dictionary, or
for a phrase the bank does not know, the nearest colour name when the similarity reaches colours.MATCH. With the
product details (details.py), a detail phrase, an "other" phrase or a phrase the bank does not know gets the detail
names it asks for ("z koronką" -> lace, lace trim), matched without its negation ("without pockets" -> pockets).
A phrase is negated when the bank says so; a phrase the bank does not know is negated when it starts with a
negation word followed by at most NEGATED_WORDS words (longer ones, such as "not in this lifetime tour", are
usually slogans).

Every phrase gives one column of percentiles within the candidates:
- an occasion, style or season phrase of the bank with concepts uses the concept scores only, when the category is
  fully scored;
- a shade with a target colour uses the closeness of the candidates' colours to it;
- a phrase with detail names uses the candidates' details (their extent), with its concepts if it has any;
- every other phrase uses text signals: TF-IDF over the name and description and the similarity of the phrase to
  the description and image embeddings, averaged; concepts of such a phrase are added, a concept matched by name
  with CONCEPT_WEIGHT against 1 for the text;
- a negated phrase is inverted, a size or audience phrase is left out.
The columns are combined with a soft AND (geometric mean). In the search UI the combined similarity of the query
breaks ties (concept scores are integers, so many candidates share one) and orders queries without a usable
phrase; on its own the ranker uses the typicality of a candidate (cosine to the mean of the candidates' description
and image embeddings) instead.
"""
from concurrent.futures import ThreadPoolExecutor
import csv
import json
import re

import numpy as np
from scipy.stats import rankdata
from sklearn.feature_extraction.text import TfidfVectorizer

import common
from concepts import PREFIX

BANK = common.SEARCH_UI / "ranking_data/phrase_bank.jsonl"
VECTORS = "bank_embeddings.npz"
NEAREST = 0.86  # chosen in the bank: from 0.86 up, the nearest other phrase shares a concept and a kind in 80% of cases
CONCEPT_MATCH = 0.80
NEGATED_WORDS = 3
CONCEPT_WEIGHT = 2.0
SHADE_IMAGE_WEIGHT = 2.0
FLOOR = 0.01
ABSTRACT = {"occasion", "style", "season"}
DETAIL_KINDS = {"detail", "other"}
UNSATISFIABLE = re.compile(r"\b(plus[- ]?size|plus|petite|tall|big and tall|maternity|pregnan\w*|nursing|\d*x+l|xxs"
                           r"|sizes?|kids?|child(ren)?|toddlers?|boys?|girls?(?! night)|juniors?|teens?|youth|baby)\b")
NEGATION = re.compile(r"^(with\s+no|without|not|no|non|bez|nie|sin)\b[\s-]*")
PREFETCH = 30  # spans of the query embedded while the parser parses
SPAN_WORDS = 3  # 92% of the residual phrases of the parser benchmark have at most 3 words, 97% are spans of the query
LONE_WORDS = {"a", "an", "the", "with", "for", "and", "or", "in", "on", "of", "to", "z", "w", "na", "i", "do", "dla"}
SHADE_WORDS = {"light", "dark", "pale", "bright", "deep", "soft", "dusty", "pastel", "neon", "hot", "baby", "ice",
               "muted", "vivid", "rich"}
COLOUR = (r"(?:black|white|gr[ae]y|blue|red|green|pink|beige|brown|yellow|orange|purple|navy|burgundy|olive|khaki|"
          r"cream|ivory|tan|camel|teal|turquoise|coral|mint|lilac|lavender|maroon|rose|wash|denim)")


def percentiles(x):
    """Rank within the candidates in (0, 1]; ties share their mean rank; a constant column is neutral (0.5)."""
    x = np.asarray(x, dtype=float)
    if x.size == 0:
        return x
    if np.ptp(x) == 0:
        return np.full(x.size, 0.5)
    return rankdata(x, method="average") / x.size


def soft_and(columns):
    """Geometric mean of per-phrase scores in [0, 1]. FLOOR keeps a single weak phrase from zeroing a product."""
    s = np.clip(np.column_stack(columns), FLOOR, 1.0)
    return np.exp(np.log(s).mean(axis=1))


def zscore(x):
    x = np.asarray(x, dtype=float)
    s = x.std()
    return (x - x.mean()) / s if s > 0 else np.zeros_like(x)


def shade_phrase(text, query):
    """"light pink" when the phrase is a lightness word ("light") that stands right before a colour ("pink") in the
    query, otherwise None."""
    if not query or text not in SHADE_WORDS:
        return None
    m = re.search(rf"\b{re.escape(text)}[\s-]+({COLOUR})\b", " ".join(query.lower().split()))
    return f"{text} {m.group(1)}" if m else None


def colour_word_before(text, query):
    """True when the phrase is a lightness word that stands right before a colour in the query."""
    return shade_phrase(text, query) is not None


def negated_text(text):
    m = NEGATION.match(text)
    return bool(m) and 0 < len(text[m.end():].split()) <= NEGATED_WORDS


def product_text(p):
    return f"{p['name']}. {p.get('description') or ''}"


def normalize_phrase(phrase):
    return " ".join(phrase.lower().split())


def load_rows(path=BANK):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def embed_bank(rows, embed, folder, workers=8):
    """Embeddings of the bank phrases (query format) in folder/VECTORS, aligned with rows; only phrases missing
    there are embedded (one API call each). -> (vectors, number of new calls)."""
    path = folder / VECTORS
    known = {}
    if path.exists():
        stored = np.load(path)
        known = dict(zip(stored["phrases"].tolist(), stored["vectors"]))
    missing = [r["phrase"] for r in rows if r["phrase"] not in known]
    with ThreadPoolExecutor(workers) as pool:
        known.update(zip(missing, pool.map(lambda p: embed(common.query_text(p)), missing)))
    phrases = [r["phrase"] for r in rows]
    vectors = common.normalize(np.stack([np.asarray(known[p], np.float32) for p in phrases]))
    np.savez(path, phrases=np.array(phrases), vectors=vectors)
    return vectors, len(missing)


class BankRanker:
    def __init__(self, products, T, I, dataset, rows, vectors, embedder, concept_categories=(), concept_ids=(),
                 concept_vectors=None, colours=None, details=None):
        self.colours, self.details = colours, details
        self.rows, self.matrix = rows, common.normalize(np.asarray(vectors, np.float32))
        self.exact = {r["phrase"]: r for r in rows}
        self.embedder, self.pool, self.prefetch_pool = embedder, ThreadPoolExecutor(8), ThreadPoolExecutor(PREFETCH)
        self.T, self.I = T, I
        self.has_image = np.linalg.norm(I, axis=1) > 0
        self.typical = common.normalize(T + I)
        corpus = []
        for split in ("train", "validation"):
            with (dataset / f"products_{split}.csv").open(newline="", encoding="utf-8") as f:
                corpus += [product_text(r) for r in csv.DictReader(f)]
        self.tfidf = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, stop_words="english").fit(corpus)
        self.tfidf_matrix = self.tfidf.transform([product_text(p) for p in products])
        self.concept_ids = list(concept_ids)
        if not isinstance(concept_categories, dict):
            concept_categories = {c: None for c in concept_categories}
        self.scored = {c: set(self.concept_ids) if v is None else set(v) for c, v in concept_categories.items()}
        self.concept_column = {c: j for j, c in enumerate(self.concept_ids)}
        self.concepts = np.array([[p.get(PREFIX + c, np.nan) for c in self.concept_ids] for p in products],
                                 dtype=float) if self.concept_ids else np.zeros((len(products), 0))
        self.concept_E = common.normalize(np.asarray(concept_vectors, np.float32)) \
            if concept_vectors is not None and len(self.concept_ids) else None

    def english(self, text):
        """The text the text signals score: the bank's English version of a known phrase, otherwise the phrase
        without its negation."""
        if text in self.exact:
            return self.exact[text]["english"]
        return text[NEGATION.match(text).end():] if negated_text(text) else text

    def detail_text(self, text):
        """The text a phrase is matched with detail names: its English version without a negation."""
        english = self.english(text)
        m = NEGATION.match(english)
        return english[m.end():] if m and english[m.end():].strip() else english

    def bank_colour(self, row):
        """Target colour of a bank shade phrase: its hex, or only its lightness."""
        if row.get("hex"):
            return dict(name=row["phrase"], hex=row["hex"], family=row.get("family"), similarity=None)
        if row.get("lightness") in ("light", "dark"):
            return dict(name=row["phrase"], lightness=row["lightness"], family=None, similarity=None)
        return None

    def colour_target(self, text, vectors):
        """Target colour of a shade text: a bank shade, a dictionary name, or the nearest dictionary name."""
        if self.colours is None:
            return None
        row = self.exact.get(text)
        if row is not None and row["kind"] == "shade" and self.bank_colour(row):
            return self.bank_colour(row)
        return self.colours.target(text, (vectors or {}).get(common.query_text(text)))

    def route(self, phrase, category, vector, query=None, vectors=None):
        """How a phrase is scored. vector: its query-format embedding (unused for a phrase found in the bank);
        query: the whole query, to read a lightness word before a colour as a shade; vectors: the embeddings of
        embed(), for the colour of a shade."""
        text = normalize_phrase(phrase)
        shade = shade_phrase(text, query)
        if shade:
            return dict(phrase=phrase, match="colour", similarity=None, neighbour=None, kind="shade", concepts=[],
                        concepts_unavailable=[], skipped=False, negated=False, english=text, text_signals=True,
                        colour=self.colour_target(shade, vectors))
        row, match, similarity, matched, colour = self.exact.get(text), "exact", None, [], None
        if row is None:
            sims = self.matrix @ vector
            j = int(np.argmax(sims))
            similarity = round(float(sims[j]), 3)
            row, match = (self.rows[j], "nearest") if sims[j] >= NEAREST else (None, "none")
        if row is not None and row["kind"] == "shade" and self.colours is not None:
            # a neighbour tells that the phrase is a shade, not which one ("ciemnozielona" is nearest to "ciemnoszary")
            colour = (self.colour_target(self.english(text), vectors) if match == "nearest" else None) \
                or self.bank_colour(row)
        if row is None and self.colours is not None:
            colour = self.colour_target(self.english(text), vectors)
            if colour:
                match, similarity = "colour name", colour["similarity"]
        detail = None
        if colour is None and self.details is not None and (row is None or row["kind"] in DETAIL_KINDS):
            detail = self.details.target((vectors or {}).get(common.query_text(self.detail_text(text))))
            if row is None and detail:
                match, similarity = "detail name", detail["similarity"]
        scored = self.scored.get(category, set())
        if row is None and colour is None and detail is None and self.concept_E is not None and scored:
            sims = np.where([c in scored for c in self.concept_ids], self.concept_E @ vector, -np.inf)
            k = int(np.argmax(sims))
            if sims[k] >= CONCEPT_MATCH:
                matched, match, similarity = [self.concept_ids[k]], "concept", round(float(sims[k]), 3)
        asked = list(row["concepts"]) if row else matched
        available = bool(asked) and all(c in scored for c in asked)
        negated = (row["negated"] if match == "exact" else negated_text(text) and row["negated"] if match == "nearest"
                   else negated_text(text))
        return dict(phrase=phrase, match=match, similarity=similarity,
                    neighbour=row["phrase"] if row and match == "nearest" else None,
                    kind=row["kind"] if row else "shade" if colour else "detail" if detail else None,
                    concepts=asked if available else [],
                    concepts_unavailable=asked if asked and not available else [],
                    skipped=bool(row and row["kind"] == "size_or_audience")
                    or (row is None and bool(UNSATISFIABLE.search(text))),
                    negated=bool(negated),
                    english=self.english(text),
                    text_signals=not (row and row["kind"] in ABSTRACT and asked and available),
                    colour=colour, detail=detail)

    def colour_score(self, r, cand):
        """Percentiles of the closeness of the candidates' colours to the phrase's target colour, or None."""
        if not r.get("colour") or self.colours is None:
            return None
        return percentiles(self.colours.score(r["colour"], cand))

    def detail_raw(self, r, cand):
        """The candidates' details the phrase asks for (extent times name weight, 0 without one), or None."""
        if not r.get("detail") or self.details is None:
            return None
        return self.details.score(r["detail"], cand)

    def text_score(self, english, cand, vectors, image_weight=1.0):
        """Weighted mean of the percentiles of TF-IDF and of the similarity to the description and image embeddings;
        the image weighs image_weight against 1 for the others."""
        self.fetch([common.query_text(english), english], vectors)
        out = []
        v = self.tfidf.transform([english])
        if v.nnz:
            out.append((1.0, percentiles((self.tfidf_matrix[cand] @ v.T).toarray().ravel())))
        out.append((1.0, percentiles(self.T[cand] @ vectors[common.query_text(english)])))
        mask = self.has_image[cand]
        if mask.any():
            out.append((image_weight, percentiles(np.where(mask, self.I[cand] @ vectors[english], -1.0))))
        return sum(w * s for w, s in out) / sum(w for w, _ in out)

    def image_weight(self, r):
        """A shade is judged mainly from the image."""
        return SHADE_IMAGE_WEIGHT if r["kind"] == "shade" else 1.0

    def phrase_column(self, r, cand, vectors):
        if r["skipped"]:
            return None
        colour = self.colour_score(r, cand)
        if colour is not None:
            return 1 - colour if r["negated"] else colour
        detail = self.detail_raw(r, cand)
        parts = [(1.0, percentiles(detail))] if detail is not None else \
            [(1.0, self.text_score(r["english"], cand, vectors, self.image_weight(r)))] if r["text_signals"] else []
        if r["concepts"]:
            raw = self.concepts[cand][:, [self.concept_column[c] for c in r["concepts"]]].mean(axis=1)
            parts.append((CONCEPT_WEIGHT if parts and r["match"] == "concept" else 1.0, percentiles(raw)))
        if not parts:
            return None
        p = sum(w * s for w, s in parts) / sum(w for w, _ in parts)
        return 1 - p if r["negated"] else p

    def prefetch(self, query):
        """Starts, before the parser returns the residual, the embeddings its phrases will probably need: every span
        of one to SPAN_WORDS words of the query (the shortest first, at most PREFETCH; a span without its negation is
        a shorter span) and, for a span the bank knows as a detail, its English version. -> {text: future}."""
        words = [w.strip(".,;:!?()\"") for w in normalize_phrase(query).split()]
        words = [w for w in words if w]
        texts = []
        for n in range(1, SPAN_WORDS + 1):
            for k in range(len(words) - n + 1):
                span = " ".join(words[k:k + n])
                if n == 1 and span in LONE_WORDS:
                    continue
                row = self.exact.get(span)
                if row is None:
                    texts.append(common.query_text(span))
                elif self.details is not None and row["kind"] in DETAIL_KINDS:
                    texts.append(common.query_text(self.detail_text(span)))
        texts = list(dict.fromkeys(texts))[:PREFETCH]
        return {t: self.prefetch_pool.submit(self.embedder, t) for t in texts}

    def embed(self, residual, query=None, text_signals=True, prefetched=None, stats=None):
        """The embeddings the phrases need, in parallel: a phrase the bank does not know (for the bank, colour, detail
        and concept names, with and without its negation), a lightness word with the colour after it ("light pink")
        for the colour names, a known detail phrase for the detail names, and with text_signals the English version
        for the descriptions (query format) and the images (plain); text_score() embeds those later when needed."""
        texts = set()
        for phrase in residual:
            text = normalize_phrase(phrase)
            shade = shade_phrase(text, query)
            if shade and self.colours is not None:
                texts.add(common.query_text(shade))
            row = self.exact.get(text)
            if row is None:
                texts |= {common.query_text(text), common.query_text(self.english(text))}
            if self.details is not None and (row is None or row["kind"] in DETAIL_KINDS):
                texts.add(common.query_text(self.detail_text(text)))
            if text_signals:
                english = self.english(text)
                texts |= {common.query_text(english), english}
        return self.fetch(texts, {}, prefetched, stats)

    def fetch(self, texts, vectors, prefetched=None, stats=None):
        """Adds the embeddings of the texts missing from vectors and returns vectors: from prefetched ({text: future},
        see prefetch) when there, the others embedded now, in parallel. stats gets phrase_embeddings_early and
        phrase_embeddings_late: how many came from prefetched and how many were embedded now."""
        prefetched = prefetched or {}
        missing = sorted(set(texts) - set(vectors))
        late = {t: self.pool.submit(self.embedder, t) for t in missing if t not in prefetched}
        early = [t for t in missing if t in prefetched]
        for t in early:
            try:
                vectors[t] = common.normalize(np.asarray(prefetched[t].result(), np.float32))
            except Exception:
                late[t] = self.pool.submit(self.embedder, t)
        for t, f in late.items():
            vectors[t] = common.normalize(np.asarray(f.result(), np.float32))
        if stats is not None:
            stats["phrase_embeddings_early"] = stats.get("phrase_embeddings_early", 0) + len(missing) - len(late)
            stats["phrase_embeddings_late"] = stats.get("phrase_embeddings_late", 0) + len(late)
        return vectors

    def adjustments(self, residual, cand, category, query=None, prefetched=None, stats=None):
        """Terms the hybrid ranking adds to the similarity of the whole query, as z-scores within the candidates:
        "concept" for an occasion, style or season phrase with concepts (or a concept matched by name), "negation"
        for a negated phrase (its concept scores, details or colour, or its text signals) to be subtracted, "colour"
        for a shade with a target colour, "detail" for a phrase with detail names. Other phrases add nothing. Every
        route gets "term": the term it went to, or None. -> (terms, routes)."""
        residual = [p for p in residual if normalize_phrase(p)]
        vectors = self.embed(residual, query, text_signals=False, prefetched=prefetched, stats=stats)
        routes = [self.route(p, category, vectors.get(common.query_text(normalize_phrase(p))), query, vectors)
                  for p in residual]
        terms = dict(concept=[], negation=[], colour=[], detail=[])
        for r in routes:
            r["term"] = None
            if r["skipped"]:
                continue
            colour, detail = self.colour_score(r, cand), self.detail_raw(r, cand)
            conceptual = bool(r["concepts"]) and (r["kind"] in ABSTRACT or r["match"] == "concept")
            if colour is not None or detail is not None:
                r["term"] = "negation" if r["negated"] else "colour" if colour is not None else "detail"
                column = zscore(colour if colour is not None else detail)
            elif conceptual:
                r["term"] = "negation" if r["negated"] else "concept"
                column = zscore(self.concepts[cand][:, [self.concept_column[c] for c in r["concepts"]]].mean(axis=1))
            elif r["negated"]:
                r["term"] = "negation"
                column = zscore(self.text_score(r["english"], cand, vectors, self.image_weight(r)))
            else:
                continue
            terms[r["term"]].append(column)
        return terms, routes

    @staticmethod
    def own_signal(r):
        """The bank scores a phrase itself only when it knows something about it: its concepts, a negation or a
        shade or detail names. Any other phrase (a theme, an unknown phrase) is better judged by the whole query."""
        return bool(r["concepts"]) or r["negated"] or r["kind"] == "shade" or bool(r.get("detail"))

    def rank(self, residual, cand, category, typicality=True, query=None, whole_query=None, prefetched=None,
             stats=None):
        """-> (scores of the candidates, routes of the phrases). typicality=False leaves ties (and all candidates when
        no phrase is usable) to the caller. whole_query(routes) -> similarity of the whole query to the candidates:
        when given, a phrase without its own signal takes that column instead of its text signals."""
        residual = [p for p in residual if normalize_phrase(p)]
        vectors = self.embed(residual, query, prefetched=prefetched, stats=stats)
        routes = [self.route(p, category, vectors.get(common.query_text(normalize_phrase(p))), query, vectors)
                  for p in residual]
        whole = None
        columns = []
        for r in routes:
            if whole_query is not None and not r["skipped"] and not self.own_signal(r):
                whole = percentiles(whole_query(routes)) if whole is None else whole
                r["whole_query"] = True
                columns.append(whole)
            else:
                c = self.phrase_column(r, cand, vectors)
                if c is not None:
                    columns.append(c)
        score = soft_and(columns) if columns else np.zeros(len(cand))
        if typicality:
            m = self.typical[cand]
            score = score + (1e-3 if columns else 1) * percentiles(m @ common.normalize(m.mean(axis=0)))
        return score, routes
