# ELF 문자열 번역. 번역 표는 translation/ko/elf_*.tsv (원문 해시 → 한국어). 원문은 원본 ELF에서 읽는다.
import os
from hk import load
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ko')
MSG = load('elf_msg')        # 메시지 표(0x100 슬롯), 5개 언어 표 모두에 적용
OPT = load('elf_opt')        # 옵션 표(0x20 슬롯)
AMMO = load('elf_ammo')      # 탄종 칸(전투 HUD 글꼴, 14음절 안에서 표기)
OTHER = load('elf_other')    # 그 밖의 문자열
HUDSTR = load('elf_hudstr')  # 전투 지휘 메뉴(전투 HUD 글꼴)
HUDCENTER = load('elf_hudcenter')  # 가운데 정렬할 항목
HUD_RANGE = (0x164c20, 0x1651d0)
HUDFORM = {}                 # 분대 지휘 항목 제목: 오프셋 → (원문 해시, 번역)
for _l in open(os.path.join(D, 'elf_hudform.tsv'), encoding='utf-8'):
    if _l.startswith('#') or not _l.strip():
        continue
    _o, _h, _k = _l.rstrip('\n').split('\t')
    HUDFORM[int(_o, 16)] = (_h, _k)
