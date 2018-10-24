from flask import request, send_from_directory, Response
from werkzeug.utils import secure_filename

from datetime import datetime
from zhlib_snapshot.level import Level
import xlsxwriter
import os
import atexit
import math

from . import app
from .dir import TEMP_DIR

level_maker = Level()


@app.route('/create', methods=['POST'])
def create_excel():
    text = request.get_json()['text']

    def _generate_base():
        for vocab_trio in level_maker.search_vocab_iter(text, format_='excel'):
            yield 'vocab', vocab_trio
        for hanzi_trio in level_maker.search_hanzi_iter(text, format_='excel'):
            yield 'hanzi', hanzi_trio

    def _generate():
        d = dict()
        for type_, (f, t, record) in _generate_base():
            d.setdefault(type_, []).append((f, t, record))
            if type_ == 'vocab':
                yield 'Loading vocab: ' + record['simplified'] + '\n'
            else:
                yield 'Loading Hanzi: ' + record['hanzi'] + '\n'

        d = {
            'hanzi': sorted(d['hanzi'], key=lambda x: x[0] if x[0] else math.inf),
            'vocab': sorted(d['vocab'], key=lambda x: -x[0])
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

        previous = 1
        format_ = None
        for i, (f, t, record) in enumerate(d['vocab']):
            if t > previous:
                previous = t
                if format_:
                    format_ = None
                else:
                    format_ = gray

            ws.write_row(i+1, 0, [
                f,
                record['simplified'],
                record.get('traditional'),
                record.get('pinyin'),
                record.get('english'),
                record.get('sentences'),
                '，'.join(record.get('tags', []) + ['tier{}'.format(t)])
            ], format_)

        ws = workbook.add_worksheet('hanzi')
        ws.freeze_panes(1, 0)
        header = [
            'Sequence',
            'Hanzi',
            'Pinyin',
            'Meaning',
            'Vocabs',
            'Sentences',
            'Tags'
        ]
        ws.write_row(0, 0, header)
        ws.set_column(0, len(header)-1, 15)

        previous = 1
        format_ = None
        for i, (f, t, record) in enumerate(d['hanzi']):
            if t > previous:
                previous = t
                if format_:
                    format_ = None
                else:
                    format_ = gray

            ws.write_row(i+1, 0, [
                f,
                record['hanzi'],
                record.get('pinyin'),
                record.get('meaning'),
                record.get('vocabs'),
                record.get('sentences'),
                '，'.join(record.get('tags', []) + ['tier{}'.format(t)])
            ], format_)

        workbook.close()

        yield filename

    return Response(_generate(), status=201)


@app.route('/excel/<filename>')
def get_excel(filename):
    filename = secure_filename(filename)
    return send_from_directory(TEMP_DIR, filename, as_attachment=True)
