from flask import request, send_from_directory, Response
from werkzeug.utils import secure_filename

from datetime import datetime
from zhlib.level import Level
import xlsxwriter
import os
import atexit
import math
import json

from . import app
from .dir import TEMP_DIR

level_maker = Level()


@app.route('/create', methods=['POST'])
def create_excel():
    text = request.get_json()['text']

    def _generate_base():
        for db_vocab in level_maker.search_vocab_iter(text):
            yield 'vocab', db_vocab
        for db_hanzi in level_maker.search_hanzi_iter(text):
            yield 'hanzi', db_hanzi

    def _generate():
        d = dict()
        for type_, record in _generate_base():
            d.setdefault(type_, []).append(record)
            yield json.dumps(record) + '\n'

        d = {
            'hanzi': sorted(d['hanzi'], key=lambda x: x['sequence'] if x['sequence'] else math.inf),
            'vocab': sorted(d['vocab'], key=lambda x: -x['frequency'])
        }

        filename = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.xlsx'
        xlsx = os.path.join(TEMP_DIR, filename)
        atexit.register(os.unlink, xlsx)

        workbook = xlsxwriter.Workbook(xlsx)
        gray = workbook.add_format({'bg_color': '#ecf0f1'})

        ws = workbook.add_worksheet('vocab')
        ws.freeze_panes(1, 0)
        header = [
            'Frequency',
            'Simplified',
            'Traditional',
            'Pinyin',
            'English',
            'Sentences',
            'Tags'
        ]
        ws.write_row(0, 0, header)
        ws.set_column(0, len(header)-1, 15)

        previous = 3.5
        format_ = None
        for i, record in enumerate(d['vocab']):
            freq_log = math.ceil(math.log10(record.get('frequency')) * 2)/2
            if 1 < freq_log < previous:
                previous = freq_log
                if format_:
                    format_ = None
                else:
                    format_ = gray

            ws.write_row(i+1, 0, [
                record.get('frequency'),
                record.get('simplified'),
                record.get('traditional', None),
                record.get('pinyin', None),
                record.get('english', None),
                '\n'.join(record.get('sentences', '')),
                ' '.join(record.get('tags', []))
            ], format_)

        ws = workbook.add_worksheet('hanzi')
        ws.freeze_panes(1, 0)
        header = [
            'Sequence',
            'Hanzi',
            'Pinyin',
            'Meaning',
            'Vocabs',
            'Sentences'
        ]
        ws.write_row(0, 0, header)
        ws.set_column(0, len(header)-1, 15)

        previous = 0
        format_ = None
        for i, record in enumerate(d['hanzi']):
            sequence = record.get('sequence')
            if not sequence or sequence > 2000:
                sequence = 10000

            current = sequence // 500
            if current > previous:
                previous = current
                if format_:
                    format_ = None
                else:
                    format_ = gray

            ws.write_row(i+1, 0, [
                record.get('sequence'),
                record.get('hanzi'),
                record.get('pinyin', None),
                record.get('meaning', None),
                '，'.join(record.get('vocabs', '')),
                '\n'.join(record.get('sentences', ''))
            ], format_)

        workbook.close()

        yield filename

    return Response(_generate(), status=201)


@app.route('/excel/<filename>')
def get_excel(filename):
    filename = secure_filename(filename)
    return send_from_directory(TEMP_DIR, filename, as_attachment=True)
