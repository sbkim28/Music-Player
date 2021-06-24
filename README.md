# Music Player

python으로 만든 music player.<br />
pyqt5를 이용해 gui를 구현한다.

## 위젯 설명
### Play List
추가한 음원 목록을 표로 보여준다.<br />
더블클릭으로 음원을 재생할 수 있다.

### Add Music Button
음원을 추가할 수 있음.
버튼을 누르고 음원을 선택한다. 한번에 여러 음원 추가가 가능하다.<br />
'-' 문자가 파일명에 1개 존재할 경우 Title과 Artist를 자동으로 분리한다.<br />

### Del Music Button
추가된 음원을 삭제할 수 있음.<br />
삭제하고 싶은 음원을 표에서 선택 후 버튼을 클릭하면 삭제가 가능하다.<br />
복수 삭제가 가능하다.

### Edit Music Button
음원의 Title과 Artist를 설정할 수 있음.<br />
바꾸고자 하는 음원을 선택 후 버튼을 클릭하면 다이얼로그가 발생한다.<br />
다이얼로그에 Title과 Artist를 입력하여 변경이 가능하다.

### Play Control (Progress Bar)
음원의 재생 progress를 알려주는 slider.<br />
slider를 움직임으로써 음원 재생 position의 변경이 가능하다.

### ◀◀ Button 
이전 음원을 재생하는 버튼 <br />
Option이 Current *로 선택되어 있다면 표에서 이전의 음원을 재생한다.<br />
Option이 All *로 선택되어 있다면 Sequence의 이전 음원을 재생한다.<br />
Option이 All Song Once이고 첫 번째 음원이라면 처음부터

### ▶ Button 
선택된 음원을 재생하는 버튼 <br />
표에서 선택된 음원을 재생한다. <br />
음원이 일시정지 상태라면 해당 음원을 다시 재생한다.

### ❚❚ Button
일시정지 버튼 <br />
현재 재생 중인 음원을 일시정지한다 <br />
재생 버튼으로 일시정지를 해제할 수 있다.

### ■ Button
정지 버튼 <br />
현재 재생 중인 음원을 정지한다. <br />

### ▶▶ Button
다음 음원을 재생하는 버튼 <br />
Option이 Current *로 선택되어 있다면 표에서 다음의 음원을 재생한다.<br />
Option이 All *로 선택되어 있다면 Sequence의 다음 음원을 재생한다.<br />
Option이 All Song Once이고 마지막 음원이라면 끝으로

### Volume
볼륨을 조절할 수 있는 slider <br />
드래그로 볼륨을 조절할 수 있다.

### Options
1. Current Song Once <br />
    현재의 곡을 1회 재생한다.
2. Current Song Loop <br />
    현재의 곡을 반복해서 재생한다.
3. All Song Once <br />
    모든 곡을 1회 순차적으로 재생한다.
4. All Song Loop <br />
    모든 곡을 반복해서 순차적으로 재생한다.
5. All Song Random <br />
    모든 곡을 반복해서 무작위로 재생한다.
   
    