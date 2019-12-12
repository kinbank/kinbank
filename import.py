#!/usr/bin/env python3
# coding=utf-8
import json
from csv import Sniffer
from collections import Counter, defaultdict
from pathlib import Path
from string import ascii_lowercase

import csvw
import pybtex
from pyglottolog import Glottolog
from clldutils.misc import slug

PARABANK = Path('./raw/parabank/raw/data/')
VARIKIN = Path('raw/varikin/lexibank_format/raw/')

KINBANK = Path('kinbank')
OUTPUT = KINBANK / 'raw'
ETCDIR = KINBANK / 'etc'

# things to not output into data file
COLS_TO_SKIP = ['glottocode', ]


OUTPUT_KEYS = [
    # IN ORDER I WANT THEM IN OUTPUT!
    'parameter',
    'word',
    'ipa',
    'description',
    'alternative',
    'source_raw',
    'source_bibtex',
    'comment',
]
EXPECTED_KEYS = OUTPUT_KEYS + ['glottocode']


JSON_KEYS = ['date of entry', 'link', 'comment', 'project']

FAMILIES = [
    'Afro-Asiatic',
    'Algic',
    'Arawakan',
    'Atlantic-Congo',
    'Austroasiatic',
    'Austronesian',
    'Cariban',
    'Central Sudanic',
    'Dravidian',
    'Indo-European',
    'Mande',
    'Nakh-Daghestanian',
    'Nilotic',
    'Nuclear Trans New Guinea',
    'Otomanguean',
    'Pama-Nyungan',
    'Pano-Tacanan',
    'Salishan',
    'Sino-Tibetan',
    'Tai-Kadai',
    'Tupian',
    'Turkic',
    'Uralic',
    'Uto-Aztecan',
]

GLOTTOLOG_CODE_UPDATE = {
    'itsa1239': 'icar1234',
    'east2283': 'nucl1235',
    'ngar1286': 'yinh1234',
}




glottolog = Glottolog("/Users/simon/src/glottolog")
glottolog = {l.id: l for l in glottolog.languoids()}


class Dataset:
    def __init__(self, label, files):
        self.label = label
        self.files = files
        # load data
        self.data = list(self.load(self._getfile('.txt')))
        # load json
        jfile = self._getfile('.json')
        if jfile:
            self.json = json.loads(jfile.read_text(encoding="utf8"))
        else:
            self.json = {}

        self._glottocode = None
    
        self.newlabel = self.label.strip().replace(" ", "_")

    def __repr__(self):
        return '<%s n=%d>' % (self.label, len(self.files))

    @property
    def glottocode(self):
        if not self._glottocode:
            glottos = set([
                r.get('glottocode') for r in self.data if r.get('glottocode')
                not in ("NA", None, "", '-')
            ])
            assert len(glottos) > 0, "No glottolog code!"
            assert len(glottos) == 1, "Multiple glottocodes %r" % glottos
            self._glottocode = glottos.pop()
            # handle the a-b-c's
            if len(self._glottocode) == 9 and self._glottocode[-1] in ascii_lowercase:
                self._glottocode = self._glottocode[0:8]

            assert len(self._glottocode) == 8, 'Malformed glottocode %r' % self._glottocode
            assert self._glottocode in self.label, 'Glottocode mismatch in name/data'
        return self._glottocode

    def _getfile(self, suffix):
        files = [f for f in self.files if f.suffix.lower() == suffix]
        if len(files) == 0:
            return None
        elif len(files) > 1:
            raise ValueError("Duplicate %s files!" % suffix)
        else:
            return files[0]

    @property
    def bib(self):
        return self._getfile('.bib')

    def fix_value(self, v):
        # "NA" in varikin means missing data
        # "#" in parabank means missing data
        if v in ('NA', '#', '-', 'NULL'):
            return ''
        else:
            return v.strip()

    def load(self, filename):
        assert filename is not None, "No datafile for %s!" % self.label
        with filename.open(encoding="utf-8-sig") as handle:
            dialect = Sniffer().sniff(handle.readline(), [',', ';'])
            dialect.doublequote = True
            handle.seek(0)
            with csvw.UnicodeDictReader(handle, dialect=dialect) as reader:
                for i, row in enumerate(reader, 2):  # 2 as row 1 is consumed for header
                    # standardise NA values.
                    try:
                        row = {k: self.fix_value(v) for (k, v) in row.items()}
                    except:
                        print("ERROR PARSING %s" % filename)
                        print("ROW %d: %r" % (i, row))
                        raise
                    
                    
                    if row['word'] == '':  # skip empty rows.
                        continue

                    # merge notes column into comment
                    try:
                        note = row.pop('notes')
                    except KeyError:
                        note = ""

                    if note:
                        if row.get("comment", "") == "":
                            row['comment'] = note
                        else:
                            print('NOTE', filename, row['comment'], note)
                            raise ValueError("Fix %s:%d manually" % (self.label, i))

                    # lose translation
                    try:
                        trans = row.pop('translation')
                    except KeyError:
                        trans = ""

                    if trans:
                        print("Value %s in `translation` will be ignored." % trans)
                        raise ValueError("Fix %s:%d manually" % (self.label, i))
                    
                    yield(row)

    def check(self):
        errors = []
        keys = [k for k in self.data[0].keys() if k not in EXPECTED_KEYS]
        if len(keys):
            errors.append("%s - ERROR - bad keys %r" % (self.label, keys))

        unknownfiles = [
            f.suffix for f in self.files if f.suffix.lower() not in 
            ('.bib', '.txt', '.json', '.ods', '.xlsx')
        ]
        if len(unknownfiles):
            errors.append(
                "%s - ERROR - extra files %r" % (self.label, unknownfiles)
            )
        return errors


    def write(self, outputdir=None):
        if not outputdir.exists():
            outputdir.mkdir()

        csvfile = outputdir / ("%s.csv" % self.newlabel)
        #bibfile = outputdir / ("%s.bib" % self.newlabel)
        #jsnfile = outputdir / ("%s.json" % self.newlabel)

        if csvfile.exists():
            raise IOError("Already Exists %s" % csvfile)

        # write text
        with csvw.UnicodeWriter(csvfile) as writer:
            writer.writerow(OUTPUT_KEYS)  # header
            for row in self.data:
                missed = [k for k in row.keys() if k not in EXPECTED_KEYS]
                if len(missed):
                    print("MISSED", self.label, missed)
                writer.writerow([row.get(h, '') for h in OUTPUT_KEYS])


def load_datasets(dirname):
    datasets = defaultdict(list)
    for p in dirname.iterdir():
        if p.stem != '.DS_Store':
            datasets[p.stem].append(p)
    return datasets


if __name__ == '__main__':
    rawdata = {"varikin": VARIKIN, 'parabank': PARABANK}
    sources = {}
    clashes = []
    languages = {}
    concepts = Counter()
    
    language_id = 1
    for dlabel, dpath in rawdata.items():
        for d in sorted(load_datasets(dpath).items()):
            try:
                ds = Dataset(*d)
            except:
                print("ERROR loading %s - %s." % d)
                raise

            if len(ds.data) == 0:
                print("EMPTY %s - ignoring." % ds)
                continue

            # check glottocode
            try:
                assert len(ds.glottocode) == 8
            except:
                print("ERROR loading %s - %s." % d)
                raise

            # patch glottocode if needed:
            ds._glottocode = GLOTTOLOG_CODE_UPDATE.get(ds.glottocode, ds.glottocode)

            if ds.newlabel in clashes:
                print("CLASH", ds.newlabel, '. Renaming to:', ds.newlabel + "a.")
                ds.newlabel = ds.newlabel + "a"
                # note that this might need to be enhanced in future if we
                # get more than one clash per language label. For now, we 
                # just check that the renaming works.
                assert ds.newlabel not in clashes, 'rename failed!'
            clashes.append(ds.newlabel)

            # check
            errors = ds.check()
            unh = [k for k in ds.json if k not in JSON_KEYS]
            if errors or unh:
                print(dlabel, ds.glottocode, ds)
                for e in errors:
                    print("\t%s" % e)
                for u in unh:
                    print("\tUNHANDLED JSON %s" % u)
                raise Exception("Unhandled Errors")

            # load sources...
            if ds._getfile('.bib'):
                bib = None
                try:
                    bib = pybtex.database.parse_file(ds._getfile('.bib'))
                except:
                    if ds._getfile('.bib').read_text() == '@{,\n\n}\n':
                        continue
                    else:
                        print("ERROR can't read %s" % ds._getfile('.bib'))
                if bib:
                    for k, b in bib.entries.items():
                        sources[k] = b

            # glottolog
            g = glottolog.get(ds.glottocode)
            if g is None:
                print("ERROR -- invalid glottocode: %s" % ds.glottocode)
                #raise ValueError("Invalid glottocode %s - %s" % (ds, ds.glottocode))
            elif g.family is None:
                outputdir = OUTPUT / 'Other'
                family = ""
            elif g.family.name in FAMILIES:
                outputdir = OUTPUT / g.family.name
                family = g.family.name
            else:
                outputdir = OUTPUT / 'Other'
                family = ""
            
            ds.write(outputdir)
            
            lid = "%s_%s" % (dlabel[0], slug(ds.newlabel))
            assert lid not in languages, 'Language ID clash - %s' % lid
            
            # store language details
            languages[lid] = {
                'ID': lid,
                'Label': ds.newlabel,
                'Glottocode': ds.glottocode,
                'ISO639P3code': g.iso,
                'Name': g.name,
                'Family': family,
                'Latitude': g.latitude,
                'Longitude': g.longitude,
                'Project': dlabel,
                'ProjectFile': ds._getfile('.txt').name,
                'EntryDate': ds.json.get("date of entry", ''),
                'Comment': ds.json.get("comment", ''),
                'Link': ds.json.get("link", ''),
            }
            language_id += 1
    
            for row in ds.data:
                concepts[(dlabel, row['parameter'])] += 1

    # write languages
    with csvw.UnicodeWriter(ETCDIR / 'languages.csv') as writer:
        header = [
            'ID', 'Label', 'Glottocode',
            'ISO639P3code', 'Name', 'Family',
            'Latitude', 'Longitude',
            'Project', 'ProjectFile',
            'EntryDate', 'Comment', 'Link'
        ]
        writer.writerow(header)
        for lang in sorted(languages):
            writer.writerow([languages[lang].get(h, '') for h in header])
    
    
    # collect all sources into one bib file.
    bib = pybtex.database.BibliographyData()
    bib.entries = sources
    bib.to_file(OUTPUT / "sources.bib")
    
    # for conc in sorted(concepts):
    #     print(conc[0], conc[1], concepts[conc])