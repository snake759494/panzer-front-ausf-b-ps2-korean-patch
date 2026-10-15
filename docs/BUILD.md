# 재빌드

Python 3.13에서 검증했습니다. 저장소 루트에 해시가 일치하는 원본을 `Panzer Front Ausf.B (Europe).iso`라는 이름으로 두고,
다음 폰트를 루트에 별도로 준비합니다. 이 파일들은 Git에서 제외됩니다.

- `DoHyeon-Regular.ttf` (배민 도현체, 본문)
- `Galmuri11-Condensed.ttf` (갈무리11 Condensed, 전투 HUD·작은 글자)
- `NanumSquareNeo-dEb.ttf`, `NanumSquareNeo-eHv.ttf` (나눔스퀘어 네오, 이미지·큰 글자)

```powershell
python -m pip install -r requirements.txt
python -X utf8 tools/prepare.py   # 원본 ISO → work/ (ELF, D.PAK 일부 추출, 로컬 전용)
python -X utf8 tools/build.py     # 원본 ISO → Panzer Front Ausf.B (Korean).iso
```

완성 ISO SHA-256은 README와 일치해야 합니다.

## 구성

- `tools/pak.py`, `tools/iso.py`, `tools/isobuild.py`: D.PAK 목차, ISO9660 레코드, 바뀐 항목을 PAK 끝에 붙이는 ISO 재작성
- `tools/pza.py`, `tools/images.py`: PZA(4/8bpp) 이미지, 글자 교체 도구
- `tools/kfont.py`: 본문 1bpp 글리프, `tools/atlas.py`: 제목·작은 글자·전투 HUD 글자 아틀라스
- `tools/build.py`: ELF 문자열·NE 메시지·SET/TNAME/DIV·폰트·이미지 적용
- `translation/hk.py`: 번역 표 로더(원문 SHA-1 앞 12자리 → 한국어), `translation/ko/*.tsv`: 번역 표
- `translation/elf_ko.py`, `extra.py`, `brief_ko.py`, `img_ko.py`, `maplabels.py`: 영역별 적용 규칙과 이미지용 한국어
- `tools/emu2.ps1`, `tools/run.sh`: PCSX2 백그라운드 자동 조작·캡처(검증용)
- `widescreen/*.pnach`: 16:9 와이드 패치

## 패치 생성/복원

```powershell
xdelta3 -e -0 -s "Panzer Front Ausf.B (Europe).iso" "Panzer Front Ausf.B (Korean).iso" Panzer_Front_AusfB_KO_v1.0.xdelta
xdelta3 -d -s "Panzer Front Ausf.B (Europe).iso" Panzer_Front_AusfB_KO_v1.0.xdelta roundtrip.iso
```

xdelta 버전/옵션에 따라 패치 바이트는 달라질 수 있지만 복원 ISO는 같아야 합니다. 생성한 게임 자료나 폰트를 커밋하지 마세요.
