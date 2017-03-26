import re
from stop_words import get_stop_words
from collections import Counter
from email.header import decode_header as decode_utf8
import pandas as pd
from scipy import sparse as sp
from sklearn.decomposition import LatentDirichletAllocation as LDA


def convert_to_utf(b):
    if type(b) == str:
        b = bytes(b, 'utf8')
    return b


def decode_part(text, typ):
    if type(text) == bytes:
        return text.decode(typ)
    else:
        return text


def combine_text_parts(parts):
    s = [decode_part(text, typ) for text, typ in parts]
    return "".join(s)


def decode_subject(s):
    try:
        out = combine_text_parts(decode_utf8(s))
    except TypeError:
        out = None
    return out


def clean(s):
    s = s.lower()
    s = re.sub(r'[^\w\s]', ' ', s)
    s = re.sub(r'[0-9]', ' ', s)
    s = re.sub(r' {2,}', ' ', s)
    s = s.strip()
    return s


def context_to_tfm(context):
    sw = set(get_stop_words('en'))
    sw = sw.union(set(['re', 'fwd', 's', 't']))
    context_term_freq = context.apply(lambda s: Counter([term for term in clean(s).split() if term not in sw]))
    term_freq = Counter()
    for b in context_term_freq:
        term_freq.update(b)
    term_id_map = {t: i for i, t in enumerate(term_freq.keys())}
    id_term_map = [t for i, t in enumerate(term_freq.keys())]
    triplet = [(freq, cid, term_id_map[term]) for cid, terms in enumerate(context_term_freq) for term, freq in
               terms.items()]
    inputs = ([d for d, _, _ in triplet], ([r for _, r, _ in triplet], [c for _, _, c in triplet]))
    return term_id_map, id_term_map, sp.csr_matrix(inputs)


def topic_terms(model,id_term_map, n_terms=20):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic %d: " % topic_idx, end='')
        print(" ".join([id_term_map[i] for i in topic.argsort()[:-n_terms - 1:-1]]))


def run_lda(filename,lda_opts,show_n_terms=10):
    raw_subjects = pd.DataFrame.from_csv(filename, sep="\t", index_col=None, header=None)
    raw_subjects.columns = ['msg_id', 'subject']
    print("Using %d emails" % len(raw_subjects))
    subjects = raw_subjects['subject'].apply(decode_subject).dropna()
    tid_map, idt_map, tfm = context_to_tfm(subjects)
    print("with %d unique terms" % len(idt_map))
    lda = LDA(**lda_opts)
    lda.fit(tfm)
    topic_terms(lda,idt_map, show_n_terms)



