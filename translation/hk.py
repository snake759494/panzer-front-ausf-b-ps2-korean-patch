"""번역 표 로더. 저장소에는 영어 원문을 넣지 않고, 원문의 SHA-1 앞 12자리를 식별자로 쓴다.
빌드할 때 원본 ISO에서 읽은 원문을 같은 방식으로 해시해 대조한다."""
import hashlib, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ko')
BSL = chr(92)


def key(s):
    return hashlib.sha1(s.encode('utf-8')).hexdigest()[:12]


def esc(s):
    return s.replace(BSL, BSL + BSL).replace('\n', BSL + 'n')


def unesc(s):
    out, i = [], 0
    while i < len(s):
        if s[i] == BSL and i + 1 < len(s):
            out.append('\n' if s[i + 1] == 'n' else s[i + 1]); i += 2
        else:
            out.append(s[i]); i += 1
    return ''.join(out)


class HDict(dict):
    """원문 문자열로 조회하면 해시 키로 바꿔 찾는 사전."""
    def __contains__(self, s): return dict.__contains__(self, key(s))
    def __getitem__(self, s): return dict.__getitem__(self, key(s))
    def get(self, s, d=None): return dict.get(self, key(s), d)


def load(name):
    h = HDict()
    for line in open(os.path.join(D, name + '.tsv'), encoding='utf-8'):
        line = line.rstrip('\n')
        if not line or line.startswith('#'):
            continue
        k, v = line.split('\t', 1)
        dict.__setitem__(h, k, unesc(v))
    return h


def save(name, d, comment=''):
    os.makedirs(D, exist_ok=True)
    with open(os.path.join(D, name + '.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        if comment:
            f.write('# ' + comment + '\n')
        for k, v in d.items():
            f.write(key(k) + '\t' + esc(v) + '\n')
