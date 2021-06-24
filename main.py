import random
import sys
import os

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

os.environ['QT_MULTIMEDIA_PREFERRED_PLUGINS'] = 'windowsmediafoundation'
DATA_FILE = './data'


class CWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.table = None
        self.volume = None
        self.progress = None
        self.current_position = None
        self.current_length = None
        self.on_edit = 0
        self.dialog_edit = None
        self.input_title = None
        self.input_artist = None
        self.grp_radio = None
        self.play_list = []
        self.player = CPlayer(self)
        self.player_state = None

        self.play_mode = 0
        self.init_ui()
        self.data_read()
        self.setting_read()

    def init_ui(self):
        window = QVBoxLayout()

        # Play List 관련 위젯.
        # Play List 목록을 관리하는 Table과 Table에 음원 파일을 추가하는 두 개의 버튼으로 구성
        list_box = QGroupBox('Play List')

        # Table
        self.table = QTableWidget(0, 2, self)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setHorizontalHeaderItem(0, QTableWidgetItem('Title'))
        self.table.setHorizontalHeaderItem(1, QTableWidgetItem('Artist'))
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.itemDoubleClicked.connect(self.table_db_clicked)

        # self.table.itemSelectionChanged.connect(None)

        # 버튼
        btn_add = QPushButton('Add Music')
        btn_add.clicked.connect(self.add_clicked)
        btn_del = QPushButton('Del Music')
        btn_del.clicked.connect(self.del_clicked)
        btn_edit = QPushButton('Edit Music')
        btn_edit.clicked.connect(self.edit_clicked)

        buttons = QHBoxLayout()
        buttons.addWidget(btn_add)
        buttons.addWidget(btn_del)
        buttons.addWidget(btn_edit)

        vbox = QVBoxLayout()
        vbox.addWidget(self.table)
        vbox.addLayout(buttons)
        list_box.setLayout(vbox)

        # 편집 다이얼로그
        self.dialog_edit = QDialog()
        self.dialog_edit.setWindowTitle('Edit Music')
        self.dialog_edit.setWindowModality(Qt.ApplicationModal)
        self.dialog_edit.resize(300, 100)

        lbl_title = QLabel('Title:')
        lbl_artist = QLabel('Artist:')

        self.input_title = QLineEdit()
        self.input_artist = QLineEdit()

        btn_edit_okay = QPushButton('OK')
        btn_edit_okay.clicked.connect(self.edit_ok_clicked)
        btn_edit_cancel = QPushButton('Cancel')
        btn_edit_cancel.clicked.connect(self.dialog_edit.close)

        dialog_grid = QGridLayout()
        dialog_grid.addWidget(lbl_title, 0, 0)
        dialog_grid.addWidget(lbl_artist, 1, 0)
        dialog_grid.addWidget(self.input_title, 0, 1)
        dialog_grid.addWidget(self.input_artist, 1, 1)

        dialog_hbox = QHBoxLayout()
        dialog_hbox.addWidget(btn_edit_okay)
        dialog_hbox.addWidget(btn_edit_cancel)

        dialog_vbox = QVBoxLayout()
        dialog_vbox.addLayout(dialog_grid)
        dialog_vbox.addLayout(dialog_hbox)

        self.dialog_edit.setLayout(dialog_vbox)

        # 음원 재생을 제어하는 위젯.
        # 이전, 재생, 일시정지, 정지, 다음 버튼과 음원 진행 상태를 나타내는 slider, volume 설정하는 slider로 구성
        control_box = QGroupBox('Play Control')

        # 음원 진행 상태를 나타내는 위젯
        self.progress = QSlider(Qt.Horizontal, self)
        self.progress.setTickPosition(QSlider.NoTicks)
        self.progress.setRange(0, 0)
        self.progress.setSingleStep(1)
        self.progress.valueChanged.connect(self.progress_value_changed)
        self.progress.sliderPressed.connect(self.progress_pressed)
        self.progress.sliderReleased.connect(self.progress_released)

        # 현재 초
        self.current_position = QLabel('00:00')
        lbl_slash = QLabel('/')
        # 재생 중인 곡의 길이
        self.current_length = QLabel('00:00')

        progress_hbox = QHBoxLayout()
        progress_hbox.addWidget(self.progress)
        progress_hbox.addWidget(self.current_position)
        progress_hbox.addWidget(lbl_slash)
        progress_hbox.addWidget(self.current_length)

        # 버튼s
        btn_prev = QPushButton('◀◀')
        btn_prev.clicked.connect(self.btn_prev_clicked)
        btn_play = QPushButton('▶')
        btn_play.clicked.connect(self.btn_play_clicked)
        btn_pause = QPushButton('❚❚')
        btn_pause.clicked.connect(self.player.pause)
        btn_stop = QPushButton('■')
        btn_stop.clicked.connect(self.btn_stop_clicked)
        btn_next = QPushButton('▶▶')
        btn_next.clicked.connect(self.btn_next_clicked)
        lbl_volume = QLabel('Volume:')

        # 볼륨 슬라이더
        self.volume = QSlider(Qt.Horizontal, self)
        self.volume.setTickPosition(QSlider.NoTicks)
        self.volume.setRange(0, 100)
        self.volume.setValue(50)
        self.volume.setSingleStep(1)
        self.volume.valueChanged[int].connect(self.volume_changed)

        button_hbox = QHBoxLayout()
        button_hbox.addWidget(btn_prev)
        button_hbox.addWidget(btn_play)
        button_hbox.addWidget(btn_pause)
        button_hbox.addWidget(btn_stop)
        button_hbox.addWidget(btn_next)
        button_hbox.addWidget(lbl_volume)
        button_hbox.addWidget(self.volume)

        vbox = QVBoxLayout()
        vbox.addLayout(progress_hbox)
        vbox.addLayout(button_hbox)
        control_box.setLayout(vbox)

        # 재생 옵션 버튼
        option_box = QGroupBox('Options')

        self.grp_radio = QButtonGroup(self)
        one_single = QRadioButton('Current Song Once')
        one_loop = QRadioButton('Current Song Loop')
        all_single = QRadioButton('All Song Once')
        all_loop = QRadioButton('All Song Loop')
        all_random = QRadioButton('All Song Random')

        self.grp_radio.addButton(one_single, 0)
        self.grp_radio.addButton(one_loop, 1)
        self.grp_radio.addButton(all_single, 2)
        self.grp_radio.addButton(all_loop, 3)
        self.grp_radio.addButton(all_random, 4)

        self.grp_radio.buttonClicked[int].connect(self.rad_clicked)
        one_single.setChecked(True)

        option_hbox = QHBoxLayout()
        option_hbox.addWidget(one_single)
        option_hbox.addWidget(one_loop)
        option_hbox.addWidget(all_single)
        option_hbox.addWidget(all_loop)
        option_hbox.addWidget(all_random)

        option_box.setLayout(option_hbox)

        window.addWidget(list_box)
        window.addWidget(control_box)
        window.addWidget(option_box)

        self.setLayout(window)
        self.setWindowTitle('Music Player')
        self.setWindowIcon(QIcon('src\\icon.png'))
        self.setGeometry(300, 300, 800, 600)
        self.show()

    # 테이블의 row가 더블클릭
    def table_db_clicked(self):
        # 더블클릭된 항목
        index = self.get_selected()
        if not index:
            index = [0]
            self.table.selectRow(0)
        # 재생, 일시정지는 고려 안함
        self.player.play(index[0], check_paused=False)

    # 추가 버튼이 눌렸을 때
    def add_clicked(self):
        # 파일 다이얼로그로 음원 파일 가져오기
        files = QFileDialog.getOpenFileNames(self, 'Add Songs', '',
                                             "Songs (*.mp3 *.wav);; mp3 File (*.mp3);; wav File(*.wav)")[0]
        cnt = len(files)
        path = [x[2] for x in self.play_list]
        add_size = 0
        row = len(self.play_list)

        # 가져온 파일들 전부 추가
        for i in range(cnt):
            # 이미 같은 링크의 파일이 존재하면 생략
            if files[i] in path:
                continue
            # 파일 이름에 따른 artist와 title 설정
            fname = os.path.splitext(files[i])
            fname = os.path.split(fname[0])[1]
            artist = ''
            d = fname.split('-')
            if len(d) == 2:
                artist, title = d
                artist = artist.rstrip()
                title = title.lstrip()
            else:
                title = fname

            item = [title, artist, files[i]]

            # 음원 리스트에 추가
            self.play_list.append(item)
            add_size += 1

        # 음원 리스트에 추가된 만큼 표 크기 늘리기
        self.table.setRowCount(row+add_size)
        for i in range(row, row + add_size):
            self.table.setItem(i, 0, QTableWidgetItem(self.play_list[i][0]))
            self.table.setItem(i, 1, QTableWidgetItem(self.play_list[i][1]))

        # 만약 player가 재생 중이면 sequence 다시 만들기
        if self.player.get_state() == QMediaPlayer.PlayingState:
            self.player.create_play_sequence(self.player.get_index())

    # 삭제 버튼이 눌렸을 때
    def del_clicked(self):
        index = self.get_selected()
        # index 고려 역순 삭제
        index.sort(reverse=True)

        for i in index:
            # 삭제하려는 음원이 재생 중이라면 Player 정지
            if self.player.get_index() == i:
                self.player.stop()

            self.table.removeRow(i)
            del self.play_list[i]

        # 만약 player가 재생 중이면 sequence 다시 만들기
        if self.player.get_state() == QMediaPlayer.PlayingState:
            self.player.create_play_sequence(self.player.get_index())

    # 편집 버튼이 눌렸을 때
    def edit_clicked(self):
        index = self.get_selected()
        if not index:
            return
        # 복수 선택시 첫 번째 편집
        self.on_edit = index[0]
        self.table.selectRow(index[0])
        self.input_title.setText(self.play_list[index[0]][0])
        self.input_artist.setText(self.play_list[index[0]][1])
        # edit dialog 보이기
        self.dialog_edit.show()

    # edit dialog에서 ok 버튼이 눌리면
    def edit_ok_clicked(self):
        title = self.input_title.text().strip()
        if not title:
            self.input_title.setFocus()
            print('\a')  # not working in ide
            return
        artist = self.input_artist.text().strip()
        if not artist:
            self.input_artist.setFocus()
            print('\a')  # not working in ide
            return
        self.play_list[self.on_edit][0] = title
        self.play_list[self.on_edit][1] = artist
        self.table.setItem(self.on_edit, 0, QTableWidgetItem(title))
        self.table.setItem(self.on_edit, 1, QTableWidgetItem(artist))
        self.dialog_edit.close()

    # 현재 선택된 row의 index 가져오기 (리스트)
    def get_selected(self):
        index = []
        for item in self.table.selectedIndexes():
            r = item.row()
            if r not in index:
                index.append(r)
        return index

    # 재생 버튼이 눌리면
    def btn_play_clicked(self):
        # 음원이 없을 경우 처리
        if not self.play_list:
            return

        index = self.get_selected()
        if not index:
            index = [0]
            self.table.selectRow(0)
        self.player.play(index[0])

    # 정지 버튼이 눌리면
    def btn_stop_clicked(self):
        # 정지
        self.player.stop()
        # 초기화
        self.current_length.setText('00:00')
        self.current_position.setText('00:00')
        self.progress.setValue(0)
        self.progress.setRange(0, 0)

    # 이전 버튼이 눌리면
    def btn_prev_clicked(self):
        # 음원이 없을 경우 처리
        if not self.play_list:
            return

        # 순차적 재생이라면 목록에서 이전으로 이동
        if self.player.sequence:
            self.player.move(-1)
        # 순서 없이 한 음원만 재생이라면 표의 이전 row로 이동
        else:
            index = self.player.get_index()
            # 값이 -1일 경우 맨 뒤로
            prev = (index - 1) % len(self.play_list)
            self.move_index(prev)

    # 다음 버튼이 눌리면
    def btn_next_clicked(self):
        # 음원이 없을 경우 처리
        if not self.play_list:
            return

        # 순차적 재생이라면 목록에서 다음으로 이동
        if self.player.sequence:
            self.player.move(1)
        # 순서 없이 한 음원만 재생이라면 표의 다음 row로 이동
        else:
            index = self.player.get_index()
            # 값이 len보다 크면 맨 앞으로
            next = (index + 1) % len(self.play_list)

            self.move_index(next)

    # 이동. player의 이동이 아닌 표에서 순서를 가지고 이동함
    def move_index(self, index, renew=True):
        self.table.selectRow(index)

        if renew:
            # 일시정지상태였다면 중지
            if self.player.get_state() == QMediaPlayer.PausedState:
                self.player.stop()
            elif self.player.get_state() == QMediaPlayer.PlayingState:
                self.player.play(index)

    # 볼륨 변경시
    def volume_changed(self):
        self.volume.setToolTip(str(self.volume.value()))
        self.player.set_volume(self.volume.value())

    # progress bar의 위치 설정
    def update_pos(self, msec):
        self.current_position.setText(self.time_format(msec // 1000))

        self.progress.blockSignals(True)
        self.progress.setValue(msec // 1000)
        self.progress.blockSignals(False)

    # 음원 길이 설정
    def update_dur(self, msec):
        self.current_length.setText(self.time_format(msec // 1000))

        self.progress.setRange(0, (msec // 1000))
        self.progress.setValue(0)
        self.current_position.setText('00:00')

    # 음원 길이 label의 텍스트 설정
    def time_format(self, sec):
        s = str(sec % 60)
        s = s.zfill(2)
        min = str((sec // 60) % 60)
        min = min.zfill(2)
        return min + ':' + s

    # progress bar의 값이 변하면
    def progress_value_changed(self):
        self.player.set_position(self.progress.value())

    # progress bar을 사용자가 누르면 음원을 일시정지함.
    def progress_pressed(self):
        # progress bar이 release 되었을 때 기존의 state를 확인하기 위한 필드
        self.player_state = self.player.get_state()
        self.player.pause()

    # progress bar이 release 되었을 때 처리
    def progress_released(self):
        # press 되기 이전의 state가 일시정지가 아니었다면 그대로 재생
        if self.player_state != QMediaPlayer.PausedState:
            # -1: 그대로 재생
            self.player.play(-1)

    # 옵션이 눌렸을 때
    def rad_clicked(self, rad_id):
        # play mode 설정
        self.player.set_play_mode(rad_id)
        # player의 상태가 정지가 아니라면 sequence 재설정
        if self.player.get_state() != QMediaPlayer.StoppedState:
            self.player.create_play_sequence(self.player.get_index())

    # 프로그램 종료시 데이터 저장
    def closeEvent(self, QCloseEvent):
        self.data_write()
        self.setting_write()
        self.deleteLater()
        QCloseEvent.accept()

    # 음원 목록 데이터 쓰기
    def data_write(self):
        with open('data', 'w', encoding='UTF-8') as f:
            for items in self.play_list:
                f.write('\t'.join(items) + '\n')
        print('data saved')

    # 음원 목록 데이터 읽기
    def data_read(self):
        if os.path.isfile('data'):
            with open('data', 'r', encoding='UTF-8') as f:
                i = 0
                data = f.readline()
                while data:
                    items = data.rstrip().split('\t')
                    self.play_list.append(items)
                    i += 1
                    data = f.readline()

            self.table.setRowCount(len(self.play_list))

            for i, items in enumerate(self.play_list):
                self.table.setItem(i, 0, QTableWidgetItem(items[0]))
                self.table.setItem(i, 1, QTableWidgetItem(items[1]))

        print('data loaded')

    # 세팅 데이터 쓰기
    def setting_write(self):
        with open('setting', 'w') as f:
            f.write('volume=' + str(self.volume.value()) + '\n')
            f.write('option=' + str(self.player.get_mode()) + '\n')
        print('setting saved')

    # 세팅 데이터 읽기
    def setting_read(self):
        if os.path.isfile('setting'):
            with open('setting', 'r') as f:
                data = f.readline()
                while data:
                    data = data.rstrip()
                    if data.startswith('volume='):
                        self.volume.setValue(int(data[7:]))
                    elif data.startswith('option='):
                        option = int(data[7:])
                        self.player.set_play_mode(option)
                        self.grp_radio.buttons()[option].setChecked(True)
                    data = f.readline()

        print('setting loaded')


# 음원 플레이어
class CPlayer:
    def __init__(self, parent):
        self.parent = parent
        self.player = QMediaPlayer()
        self.player.setVolume(50)
        self.player.durationChanged.connect(self.duration_changed)
        self.player.positionChanged.connect(self.position_changed)
        self.player.stateChanged.connect(self.state_changed)
        self.sequence = []
        self.index = 0
        self.mode = 0

    # 음원 순서 목록 만들기
    def create_play_sequence(self, index):
        # 순차적 재생 모드가 아니라면 sequence를 비움
        if self.mode == 0 or self.mode == 1:
            self.sequence = []
            return
        size = len(self.parent.play_list)
        # 시작점부터
        self.sequence = [x % size for x in range(index, index + len(self.parent.play_list))]
        # 랜덤 모드일 때 초항 제외 무작위 정렬
        if self.mode == 4:
            _t = self.sequence[1:]
            random.shuffle(_t)
            self.sequence = self.sequence[:1] + _t

    # >> or << 버튼으로 또는 곡이 끝나서 이동함
    def move(self, direction):
        # parent 음원 리스트의 인덱스를 이용해 현 sequence 위치 찾기
        cur_index = self.sequence.index(self.index)
        size = len(self.sequence)
        cur_index += direction
        # 모드가 1번만 재생이라면 시작과 끝의 처리
        if self.mode == 2:
            if cur_index < 0:
                self.player.setPosition(0)
                return
            elif cur_index >= size:
                self.player.setPosition(self.player.duration())
                return
        else:
            cur_index = cur_index % size
        self.index = self.sequence[cur_index]
        # table의 포커스만 이동, 갱신은 안함
        self.parent.move_index(self.index, renew=False)
        self.set_media()

    # 재생 check_paused: 일시정지 상태 고려 여부
    def play(self, index, check_paused=True):
        # 그대로 재생일때
        if index == -1:
            self.player.play()
            return

        # 일시정지 상태였다면 그대로 재생,
        if self.player.state() == QMediaPlayer.PausedState and check_paused:
            self.player.play()
            self.parent.table.selectRow(self.index)
        else:
            # sequence 만들기
            self.create_play_sequence(index)
            self.index = index
            self.set_media()

    # 일시정지
    def pause(self):
        self.player.pause()

    # 정지
    def stop(self):
        self.player.blockSignals(True)
        self.player.stop()
        self.player.blockSignals(False)
        self.player.sequence = []

    # 음원 설정 후 재생
    def set_media(self):
        url = QUrl.fromLocalFile(self.parent.play_list[self.index][2])
        content = QMediaContent(url)
        # 음원 설정 시 player의 신호 차단
        self.player.blockSignals(True)
        self.player.setMedia(content)
        self.player.blockSignals(False)
        self.player.play()

    # 볼륨 설정
    def set_volume(self, vol):
        self.player.setVolume(vol)

    # progress bar을 통한 position 설정
    def set_position(self, sec):
        msec = sec * 1000
        self.player.setPosition(msec)

    # 음원이 변경되어 곡의 길이가 변했을 때
    def duration_changed(self, msec):
        if msec > 0:
            self.parent.update_dur(msec)

    # 재생 도중 위치의 변경
    def position_changed(self, msec):
        if msec > 0:
            self.parent.update_pos(msec)

    # 상태가 변했을 때 - 곡이 끝날 때를 감지하는 용도로 사용
    def state_changed(self):
        if self.player.state() == QMediaPlayer.StoppedState:
            if self.mode == 0:  # cur once
                return
            elif self.mode == 1:  # cur loop
                self.parent.update_pos(0)
                self.player.play()
            else:
                self.move(1)

    def set_play_mode(self, mode):
        self.mode = mode

    def get_index(self):
        return self.index

    def get_state(self):
        return self.player.state()

    def get_mode(self):
        return self.mode


def main():
    app = QApplication(sys.argv)
    ex = CWidget()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
