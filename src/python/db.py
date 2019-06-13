import sqlite3
import pinyin
from wordfreq import word_frequency


class Db:
    def __init__(self):
        self.conn = sqlite3.connect("asset/zh.db", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def get_vocab(self, v: str) -> dict:
        ds = [dict(c) for c in self.conn.execute("""
        SELECT
            simplified,
            traditional,
            pinyin,
            english,
            tag,
            frequency
        FROM
            vocab
        WHERE
            simplified = ?
        """, (v,)).fetchall()]

        if len(ds) > 0:
            d = ds[0]
        else:
            d = {
                "simplified": v,
                "pinyin": pinyin.get(v, delimiter=" ", format="numerical"),
                "frequency": word_frequency(v, "zh")
            }

        d["sentence"] = [dict(c) for c in self.conn.execute("""
        SELECT
            chinese,
            english
        FROM
            sentence
        WHERE
            chinese LIKE ?
        ORDER BY frequency DESC
        """, (f"%{v}%",)).fetchmany(10)]

        return d

    def get_hanzi(self, h: str) -> dict:
        ds = [dict(c) for c in self.conn.execute("""
        SELECT
            entry,
            pinyin,
            english,
            percentile
        FROM
            hanzi
        WHERE
            entry = ?
        """, (h,)).fetchall()]

        if len(ds) > 0:
            d = ds[0]
        else:
            d = {
                "entry": h,
                "pinyin": pinyin.get(h, delimiter=" ", format="numerical")
            }

        d["vocab"] = [dict(c) for c in self.conn.execute("""
        SELECT DISTINCT
            simplified
        FROM
            vocab
        WHERE
            simplified LIKE ? OR
            traditional LIKE ?
        ORDER BY frequency DESC
        """, (f"%{h}%", f"%{h}%")).fetchmany(10)]

        d["sentence"] = [dict(c) for c in self.conn.execute("""
        SELECT
            chinese,
            english
        FROM
            sentence
        WHERE
            chinese LIKE ?
        ORDER BY frequency DESC
        """, (f"%{h}%",)).fetchmany(10)]

        return d


db = Db()
