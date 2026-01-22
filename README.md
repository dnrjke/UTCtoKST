# UTC <-> KST Converter 🕒

PyQt5 기반의 현대적이고 직관적인 UTC-KST 시간 변환 및 시각화 도구입니다.

![App Preview](assets/preview.png)

## ✨ 주요 기능
- **듀얼 타임라인**: UTC와 KST 시간을 한눈에 비교할 수 있는 24시간 가로 스크롤 뷰를 제공합니다.
- **자동 동기화**: 현재 UTC 시간을 기준으로 타임라인이 자동으로 정렬됩니다.
- **스마트 테마**: 시간대(낮/밤/전환기)에 따라 슬롯의 색상이 자동으로 변경됩니다.
- **상세 정보 표시**: 타임라인 슬롯 클릭 시 선택된 시간과 현재 시점으로부터의 상대적인 차이(예: "in 2 hours", "1 hour ago")를 색상별로 구분하여 표시합니다.
- **시스템 트레이 상주**: 창을 닫아도 트레이 아이콘으로 유지되어 배경에서 계속 작동하며, 필요할 때 즉시 호출할 수 있습니다.
- **중복 실행 방지**: 프로그램이 이미 실행 중일 때 다시 실행하면 기존 인스턴스를 활성화하여 중복 실행을 막습니다.

## 🚀 시작하기

### 실행 파일 (Windows 전용)
파이썬 설치 없이 바로 사용하려면 [Releases](https://github.com/사용자아이디/UTCtoKST/releases) 페이지에서 `UTCtoKST.exe`를 다운로드하여 실행하세요.

### 소스 코드로 실행
파이썬(3.8 이상)이 설치된 환경에서 아래 명령어를 실행하세요.

1. **저장소 복제**
   ```bash
   git clone https://github.com/사용자아이디/UTCtoKST.git
   cd UTCtoKST
   ```

2. **필수 라이브러리 설치**
   ```bash
   pip install PyQt5
   ```

3. **프로그램 실행**
   ```bash
   python UTCtoKST.py
   ```

## 🛠 기술 스택
- **Language**: Python 3.x
- **UI Framework**: PyQt5
- **Build Tool**: PyInstaller

## 📄 라이선스
이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자유롭게 수정 및 배포가 가능합니다.

