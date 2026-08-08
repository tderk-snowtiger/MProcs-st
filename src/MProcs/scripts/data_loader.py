import json
import os

_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def _load(name):
    path = os.path.join(_data_dir, f'{name}.json')
    with open(path, encoding='utf-8') as f:
        return json.load(f)


katakana = _load('katakana')
jamo = _load('jamo')
chi_chars = _load('chi_chars')
proverbs = _load('proverbs')
diction = _load('diction')
acadlist = _load('acadlist')
dhammapada1 = _load('dhammapada1')
medicals1 = _load('medicals1')
mims = _load('mims')
science1 = _load('science1')
psychology1 = _load('psychology1')
biology1 = _load('biology1')
chemistry1 = _load('chemistry1')
legal_terms1 = _load('legal_terms1')
degrees1 = _load('degrees1')
verses1 = _load('verses1')
bible1 = _load('bible1')
koran1 = _load('koran1')
fcci = _load('fcci')
hospitals = _load('hospitals')
tracks = _load('tracks')
strains = _load('strains')
