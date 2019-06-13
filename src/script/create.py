import sqlite3
from wordfreq import word_frequency
import jieba

if __name__ == "__main__":
    conn = sqlite3.connect("asset/zh.db")

    # for h_id, entry, tag in conn.execute("SELECT id, entry, tag FROM hanzi"):
    #     if tag:
    #         conn.execute("UPDATE vocab SET tag = ? WHERE simplified = ? OR traditional = ?",
    #                      (tag, entry, entry))
    #     if len(entry) > 1:
    #         conn.execute("DELETE FROM hanzi WHERE id = ?", (h_id,))

    # conn.commit()

    with open("asset/junda.tsv") as f:
        for row in f:
            serial, c, count, percentile, pinyin, english, *_ = (row[:-1] + "\t\t\t\t\t\t").split("\t")

            count = int(count) if count else None
            percentile = float(percentile) if percentile else None
            if not pinyin:
                pinyin = None
            if not english:
                english = None

            try:
                conn.execute("""
                INSERT INTO hanzi (entry, count, percentile, pinyin, english)
                VALUES (?, ?, ?, ?, ?)
                """, (c, count, percentile, pinyin, english))
            except sqlite3.Error:
                conn.execute("""
                UPDATE hanzi SET count = ?, percentile = ?, pinyin = ?, english = ?
                WHERE entry = ?
                """, (count, percentile, pinyin, english, c))

    conn.commit()

    for c_id, s in conn.execute("SELECT id, simplified FROM vocab"):
        conn.execute("""
        UPDATE vocab SET frequency = ? WHERE id = ?
        """, (word_frequency(s, "zh") * 10**6, c_id))

    for s_id, chinese in conn.execute("SELECT id, chinese FROM sentence"):
        conn.execute("""
        UPDATE sentence SET frequency = ? WHERE id = ?
        """, (min(word_frequency(s, "zh") * 10**6 for s in set(jieba.cut(chinese))), s_id))

    conn.commit()
    conn.close()
