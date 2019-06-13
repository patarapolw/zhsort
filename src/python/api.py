from flask import Blueprint, request, Response
import jieba
import json
import regex

from .db import db

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/generate", methods=["POST"])
def r_create():
    entry = request.json["entry"]

    def _generate():
        yield "vocab\n"

        for v in set(s for s in jieba.cut(entry) if regex.search("\\p{IsHan}", s)):
            yield json.dumps(db.get_vocab(v), ensure_ascii=False) + "\n"

        yield "hanzi\n"

        for h in set(regex.sub("[^\\p{IsHan}]", "", entry)):
            yield json.dumps(db.get_hanzi(h), ensure_ascii=False) + "\n"

    return Response(_generate())
