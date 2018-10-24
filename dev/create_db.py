from tqdm import tqdm
from zhlib_snapshot import db
from wordfreq import word_frequency
from zhlib import db as zh


if __name__ == '__main__':
    db.database.create_tables([db.Vocab, db.Hanzi])

    for zh_vocab in tqdm(zh.Vocab.select()):
        db.Vocab.create(
            id=zh_vocab.id,
            simplified=zh_vocab.simplified,
            traditional=zh_vocab.traditional,
            pinyin=zh_vocab.pinyin,
            english=zh_vocab.english,
            frequency=word_frequency(zh_vocab.simplified, 'zh'),
            tags=[t.name for t in zh_vocab.tags],
            sentences=[s.sentence for s in zh_vocab.get_sentences()]
        )

    for zh_hanzi in tqdm(zh.Hanzi.select()):
        db.Hanzi.create(
            id=zh_hanzi.id,
            hanzi=zh_hanzi.hanzi,
            pinyin=zh_hanzi.pinyin,
            meaning=zh_hanzi.meaning,
            heisig=zh_hanzi.heisig,
            kanji=zh_hanzi.kanji,
            junda=zh_hanzi.junda,
            tags=[t.name for t in zh_hanzi.tags],
            vocabs=[v.simplified for v in zh_hanzi.get_vocabs()],
            sentences=[s.sentence for s in zh_hanzi.get_sentences()]
        )
