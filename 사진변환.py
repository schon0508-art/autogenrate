from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from 문구만들기 import 문구만들기

크기 = 1080
기준폴더 = Path(__file__).parent
자료폴더 = 기준폴더 / "자료"
완성폴더 = 기준폴더 / "완성"

자료폴더.mkdir(exist_ok=True)
완성폴더.mkdir(exist_ok=True)

오늘 = date.today().isoformat()

정보파일 = 자료폴더 / "가게 정보.txt"
if 정보파일.exists():
    문구만들기(정보파일, 완성폴더 / "홍보문구.txt")
    print("홍보 문구를 '완성' 폴더에 홍보문구.txt로 저장했어요.")
else:
    print("'자료' 폴더에 '가게 정보.txt'가 없어서 문구 만들기는 건너뛰었어요.")

로고경로 = 자료폴더 / "로고.png"
로고 = None
if 로고경로.exists():
    with Image.open(로고경로) as 로고원본:
        로고 = 로고원본.convert("RGBA")
    # 흰 판까지 포함해서 사진 가로의 15%
    판너비 = int(크기 * 0.15)
    판여백 = 12
    로고너비 = 판너비 - 판여백 * 2
    로고높이 = int(로고.height * 로고너비 / 로고.width)
    로고 = 로고.resize((로고너비, 로고높이), Image.LANCZOS)
    # 로고 뒤에 둥근 흰색 사각 판 (90% 진하기)
    판 = Image.new("RGBA", (판너비, 로고높이 + 판여백 * 2), (0, 0, 0, 0))
    ImageDraw.Draw(판).rounded_rectangle(
        (0, 0, 판.width - 1, 판.height - 1), radius=10, fill=(255, 255, 255, 230)
    )
    판.alpha_composite(로고, (판여백, 판여백))
    로고 = 판

사진목록 = sorted(
    p
    for p in 자료폴더.iterdir()
    if p.suffix.lower() in (".jpg", ".jpeg", ".png") and p.name != "로고.png"
)

if not 사진목록:
    print("'자료' 폴더에 사진이 없어요. jpg나 png 사진을 넣고 다시 실행해주세요.")
    raise SystemExit

# 오늘 이미 만든 번호가 있으면 이어서 번호를 붙인다
번호 = 1
while (완성폴더 / f"{오늘}_{번호:02d}.jpg").exists():
    번호 += 1

for 사진 in 사진목록:
    with Image.open(사진) as 원본:
        그림 = ImageOps.exif_transpose(원본)  # 휴대폰 사진 방향 바로잡기
        그림 = 그림.convert("RGB")
        # 가운데 기준으로 정사각형 자르기 + 1080 크기로 맞추기 (찌그러짐 없음)
        결과 = ImageOps.fit(그림, (크기, 크기), Image.LANCZOS, centering=(0.5, 0.5))
        if 로고 is not None:
            여백 = 40
            위치 = (크기 - 로고.width - 여백, 크기 - 로고.height - 여백)
            결과.paste(로고, 위치, 로고)
        저장경로 =완성폴더 / f"{오늘}_{번호:02d}.jpg"
        결과.save(저장경로, "JPEG", quality=95)
    print(f"{사진.name} -> {저장경로.name}")
    번호 += 1

print(f"끝! 사진 {len(사진목록)}장을 '완성' 폴더에 저장했어요.")
