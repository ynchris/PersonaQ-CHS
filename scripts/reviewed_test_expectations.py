"""Independent author-file expectations for tests spanning successive batches."""
import hashlib
from functools import lru_cache
from compile_translation import ROOT,read,LEADING,TRAILING

@lru_cache(None)
def corrections():
    return {r['key']:r for r in read(ROOT/'translation/text_corrections.review.json')['rows']}

def before_review(key,current):
    row=corrections().get(key)
    if row:
        assert current==row['after'], f'Unreviewed modification: {key}'
        return row['before']
    return current

@lru_cache(None)
def authored_rows(source):
    result={};source_hash=hashlib.sha256((ROOT/source).read_bytes()).hexdigest()
    doc=read(ROOT/source)
    for path in sorted((ROOT/'translation/batches').glob('*.json')):
        batch=read(path)
        for mi,li,mid,body in batch['sources'].get(source,[]):
            # Earliest manually authored batches predate source-hash metadata;
            # their message IDs are still checked. Later pinned batches must
            # continue to match the original export hash exactly.
            if source in batch.get('source_hashes',{}):
                assert batch['source_hashes'][source]==source_hash
            assert (mi,li) not in result
            assert doc['texts'][mi]['id']==mid
            original=doc['texts'][mi]['lines'][li]
            result[mi,li]=LEADING.match(original).group()+body+TRAILING.search(original).group()
    return result

def authored_translation(source,mi,li,original):
    value=authored_rows(source).get((mi,li),original)
    correction=corrections().get(f'{source}:{mi}:{li}')
    if correction:
        assert value==correction['before'] and original==correction['original']
        return correction['after']
    return value
