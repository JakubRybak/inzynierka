"""
Soft phrase signals tried in the experiments (variants.py): a residual phrase is compared with the colour names, the
detail names and the concept names of a product without thresholds or routes. The similarity of the phrase to a name
counts by how far it is above the phrase's median similarity to all names of that kind, like the sentence signal of
the search UI (search_ui/core/sentences.py).
"""
import numpy as np
import pandas as pd

from evaluate import colours


def excess(sims):
    return np.maximum(sims - np.median(sims), 0)


class Soft:
    def __init__(self, engine):
        bank = engine.bank
        self.colours, self.details = bank.colours, bank.details
        position = {p["product_id"]: i for i, p in enumerate(engine.products)}
        column = {n: j for j, n in enumerate(self.colours.names)}
        self.colour_name = np.full((len(engine.products), colours.SLOTS), -1)
        for r in pd.read_parquet(colours.PRODUCTS).itertuples():
            i = position.get(r.product_id)
            if i is not None and r.rank < colours.SLOTS:
                self.colour_name[i, r.rank] = column.get(r.name, -1)
        self.concept_E, self.concept_scores = bank.concept_E, np.nan_to_num(bank.concepts) / 10

    def colour(self, v, cand):
        """Share-weighted similarity of the phrase to the candidate's colour names."""
        e = np.append(excess(self.colours.E @ v), 0.0)
        return (self.colours.share[cand] * e[self.colour_name[cand]]).sum(axis=1)

    def detail(self, v, cand):
        """The candidate's best detail: its extent times the similarity of the phrase to its name."""
        return (self.details.W[cand] * excess(self.details.E @ v)).max(axis=1)

    def concept(self, v, cand):
        """Concept scores of the candidate weighted by the similarity of the phrase to the concept names."""
        return self.concept_scores[cand] @ excess(self.concept_E @ v)
