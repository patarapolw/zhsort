import XLSX from "xlsx";

export interface IExport {
    hanzi: any[];
    vocab: any[];
}

export async function createExcel(data: IExport, cb: (x: string) => any) {
    const wb = XLSX.utils.book_new();

    (() => {
        const aoa: any[][] = [];
        aoa.push([
            'Frequency',
            'Simplified',
            'Traditional',
            'Pinyin',
            'English',
            'Sentences',
            'Tags'
        ]);

        for (const d of data.vocab.sort((a, b) => (b.frequency || -1) - (a.frequency || -1))) {
            aoa.push([
                d.frequency,
                d.simplified,
                d.traditional,
                d.pinyin,
                d.english,
                d.sentence.map((s: any) => `${s.chinese} ${s.english}`).join("\n"),
                d.tag
            ]);
        }

        const ws = XLSX.utils.aoa_to_sheet(aoa);
        XLSX.utils.book_append_sheet(wb, ws, "vocab");
    })();

    (() => {
        const aoa: any[][] = [];

        aoa.push([
            'Percentile',
            'Hanzi',
            'Pinyin',
            'English',
            'Vocabs',
            'Sentences',
            'Tags'
        ]);

        for (const d of data.hanzi.sort((a, b) => (a.percentile || 100) - (b.percentile || 100))) {
            aoa.push([
                d.percentile,
                d.entry,
                d.pinyin,
                d.english,
                d.vocab.map((v: any) => v.simplified).join(", "),
                d.sentence.map((s: any) => `${s.chinese} ${s.english}`).join("\n"),
                d.tag
            ]);
        }

        const ws = XLSX.utils.aoa_to_sheet(aoa);
        XLSX.utils.book_append_sheet(wb, ws, "hanzi");
    })();

    XLSX.writeFile(wb, "sorted.xlsx");
}
