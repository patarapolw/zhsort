import peewee as pv
from playhouse import sqlite_ext
from playhouse.shortcuts import model_to_dict
from pathlib import Path

database = sqlite_ext.SqliteDatabase(str(Path(__file__).with_name('dict.db')), pragmas={
    # 'query_only': 'ON'
})


class BaseModel(pv.Model):
    class Meta:
        database = database


class Hanzi(BaseModel):
    hanzi = pv.TextField(unique=True)
    pinyin = pv.TextField(null=True)
    meaning = pv.TextField(null=True)
    heisig = pv.IntegerField(null=True)
    kanji = pv.TextField(null=True)
    junda = pv.IntegerField(null=True, unique=True)
    vocabs = sqlite_ext.JSONField(default=list)
    sentences = sqlite_ext.JSONField(default=list)
    compositions = sqlite_ext.JSONField(default=list)
    supercompositions = sqlite_ext.JSONField(default=list)
    variants = sqlite_ext.JSONField(default=list)
    tags = sqlite_ext.JSONField(default=list)

    cache = dict()

    def __str__(self):
        return '{hanzi} {pinyin} {meaning}'.format(**dict(
            hanzi=self.hanzi,
            pinyin=('[{}]'.format(self.pinyin) if self.pinyin else ''),
            meaning=(self.meaning if self.meaning else '')
        ))

    def to_excel(self):
        d = model_to_dict(self)
        d.update({
            'vocabs': '，'.join(d['vocabs']),
            'sentences': '\n'.join(d['sentences']),
            'compositions': '，'.join(d['compositions']),
            'supercompositions': '，'.join(d['supercompositions']),
            'variants': '，'.join(d['variants']),
            'tags': d['tags']
        })

        return d


class Vocab(BaseModel):
    simplified = pv.TextField()
    traditional = pv.TextField(null=True)
    pinyin = pv.TextField(null=True)
    english = pv.TextField(null=True)
    frequency = pv.FloatField()
    # hanzis = sqlite_ext.JSONField(default=list)
    sentences = sqlite_ext.JSONField(default=list)
    tags = sqlite_ext.JSONField(default=list)

    class Meta:
        indexes = (
            (('simplified', 'traditional', 'pinyin', 'english'), True),
        )

    def __str__(self):
        return '{simplified} {traditional} {pinyin} {english}'.format(**dict(
            simplified=self.simplified,
            traditional=(self.traditional if self.traditional else ''),
            pinyin=('[{}]'.format(self.pinyin) if self.pinyin else ''),
            english=(self.english if self.english else '')
        ))

    @classmethod
    def match(cls, vocab):
        return cls.select().where((cls.simplified == vocab) | (cls.traditional == vocab))

    def to_excel(self):
        d = model_to_dict(self)
        d.update({
            'frequency': d['frequency'] * 10 ** 6,
            'sentences': '\n'.join(d['sentences']),
            'tags': d['tags']
        })

        return d
