import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from clldutils.misc import slug
from pylexibank import Dataset as BaseDataset
from pylexibank import Language, Concept, FormSpec


@dataclass
class CustomLanguage(Language):
    Label: Optional[str] = None
    Project: Optional[str] = None
    ProjectFile: Optional[str] = None
    ProjectName: Optional[str] = None
    EntryDate: Optional[str] = None
    Comment: Optional[str] = None
    Link: Optional[str] = None
    Set: Optional[str] = None


@dataclass
class CustomConcept(Concept):
    Parameter: Optional[str] = None
    Group: Optional[str] = None
    Dataset: Optional[str] = None


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "kinbank"
    language_class = CustomLanguage
    concept_class = CustomConcept
    
    form_spec = FormSpec(
        brackets={"[": "]", "{": "}", "(": ")", "‘": "’"},
        separators=";/,",
        missing_data=('?', '-', '', ''),
        strip_inside_brackets=True
    )
    
    def cmd_makecldf(self, args):
        languages = args.writer.add_languages(
            lookup_factory='Label'
        )

        concepts = args.writer.add_concepts(
            id_factory=lambda c: c.id,
            lookup_factory="Parameter"
        )

        for filename in sorted(self.raw_dir.glob("*/*.csv")):
            
            try:
                lang_id = languages[filename.stem]
            except KeyError as e:
                raise KeyError("Unable to find %s in `Label` column of ./etc/languages.csv." % filename)
                
            for lineid, row in enumerate(self.raw_dir.read_csv(filename, dicts=True), 1):
                try:
                    concept_id = concepts.get(row['parameter'].strip(), row['parameter'].strip())
                except Exception as e:
                    raise Exception("Error getting concept_id on line %d for %s:%s" % (
                        lineid, filename, row.get('parameter', None)
                    ))

                # default to IPA column if present otherwise use word column
                value = row['ipa'] if len(row['ipa']) else row['word']
                if value:
                    lex = args.writer.add_forms_from_value(
                        Language_ID=lang_id,
                        Parameter_ID=concept_id,
                        Value=value.strip(),
                        Comment=row['comment'],
                        Source=row['source_bibtex'],
                    )
        
        args.writer.add_sources()
