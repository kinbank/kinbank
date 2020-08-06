import json
from pathlib import Path

import attr
from clldutils.misc import slug
from pylexibank import Dataset as BaseDataset
from pylexibank import Language, Concept, FormSpec


@attr.s
class CustomLanguage(Language):
    Label = attr.ib(default=None)
    Project = attr.ib(default=None)
    ProjectFile = attr.ib(default=None)
    ProjectName = attr.ib(default=None)
    EntryDate = attr.ib(default=None)
    Comment = attr.ib(default=None)
    Link = attr.ib(default=None)


@attr.s
class CustomConcept(Concept):
    Parameter = attr.ib(default=None)
    Group = attr.ib(default=None)
    Dataset = attr.ib(default=None)


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
            lang_id = languages[filename.stem]
            for lineid, row in enumerate(self.raw_dir.read_csv(filename, dicts=True), 1):
                try:
                    concept_id = concepts.get(row['parameter'], row['parameter'])
                except Exception as e:
                    print("Error getting concept_id on line %d for %s:%s" % (lineid, filename, row['parameter']))
                    raise

                # default to IPA column if present otherwise use word column
                value = row['ipa'] if len(row['ipa']) else row['word']
                if value:
                    lex = args.writer.add_forms_from_value(
                        Language_ID=lang_id,
                        Parameter_ID=concept_id,
                        Value=value,
                        Comment=row['comment'],
                        Source=row['source_bibtex'],
                    )
        
        args.writer.add_sources()
