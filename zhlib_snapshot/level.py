from wordfreq import word_frequency
import math

from . import db
from .util import find_hanzi, find_vocab


class Level:
    TIER_MIN = 1
    TIER_MAX = 6

    @classmethod
    def hanzi_get_level(cls, hanzi):
        db_hanzi = db.Hanzi.get_or_none(hanzi=hanzi)
        if db_hanzi:
            return db_hanzi.junda

    def search_text(self, text, format_='excel'):
        return {
            'hanzi': sorted(self.search_hanzi_iter(text, format_=format_),
                            key=lambda x: x[0] if x[0] else math.inf),
            'vocab': sorted(self.search_vocab_iter(text, format_=format_),
                            key=lambda x: -x[0])
        }

    def search_hanzi_iter(self, text, format_=None):
        for hanzi in find_hanzi(text):
            level = self.hanzi_get_level(hanzi)
            if level:
                tier = self.normalize(level // 400 + 1)
            else:
                tier = self.TIER_MAX

            db_hanzi = db.Hanzi.get_or_none(hanzi=hanzi)
            if db_hanzi:
                if format_ == 'excel':
                    yield level, tier, db_hanzi.to_excel()
                else:
                    yield level, tier, db_hanzi
            else:
                yield level, tier, dict(hanzi=hanzi)

    def search_vocab_iter(self, text, format_=None):
        for vocab in find_vocab(text):
            freq = word_frequency(vocab, 'zh') * 10**6
            try:
                tier = self.normalize(8 - (math.log10(freq) * 2))
            except ValueError:
                tier = self.TIER_MAX

            db_vocabs = db.Vocab.match(vocab)
            if len(db_vocabs) > 0:
                if format_ == 'excel':
                    yield freq, tier, db_vocabs[0].to_excel()
                else:
                    yield freq, tier, db_vocabs[0]
            else:
                yield freq, tier, dict(simplified=vocab)

    @classmethod
    def normalize(cls, tier):
        tier = int(tier)
        if tier < cls.TIER_MIN:
            return cls.TIER_MIN
        elif tier > cls.TIER_MAX:
            return cls.TIER_MAX

        return tier
