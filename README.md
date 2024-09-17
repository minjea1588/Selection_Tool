# Selection_Tool
영역을 지정하는 라벨링 툴입니다.

## 환경설정
pip install -r requirements.txt

## 실행명령어
python Selection_Tool.py

## 기능설명
1. Upload Image 
    - 이미지 업로드 기능입니다.
    - jpg, png 가능합니다.

2. Draw Box
    - 박스를 그립니다.
    - 4개의 점을 찍으면 class를 선택하여 지정할 수 있습니다.

3. Save
    - 박스를 전부 그린 후, json으로 box정보 저장합니다.
    - yaml로 class 정보를 load 하면, class_info 로 class 정보도 저장합니다.

4. Reset View
    - 이미지를 중앙으로 오게 합니다

5. Load Classes
    - class를 Load합니다
    - yaml과 txt 파일 지원하며, class.txt, class.yaml 형태로 작성해서 Load 해주시면 됩니다.

6. Remove Last Box
    - 최근 그렸던 박스를 이미지에서 삭제합니다.

7. Rectangular Mode
    - 평행한 선으로 직사각형을 그릴 수 있습니다.

8. 단축키
    - B : Draw Box 활성화
    - Ctrl + z : Remove Last Box 클릭

9. 기타
    - 마우스 드래그로 이미지 내에 이동 가능
    - 확대 축소 가능

## 추가예정 기능
 1. json파일 로드해서 보기
 2. 박스 수정기능
