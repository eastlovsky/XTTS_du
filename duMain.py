# This Python file uses the following encoding:utf-8
# coding:utf-8
import pypinyin
import Image
from pypinyin import slug
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from du_ui import *
from aip import AipSpeech, AipOcr
from ctypes import windll
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class mciThread(QThread):   # 播放声音线程
    def __init__(self, parent, s):
        super(mciThread, self).__init__(parent)
        self.sound = s

    def run(self):
        def mci(s):
            i = windll.winmm.mciSendStringA(s, 0, 0, 0)
            if not i == 0:
                print "Error %d in mciSendString %s" % (i, s)

        open_info = 'open "' + self.sound + '" alias music'
        mci(open_info)
        mci('play music')
        mci("play music wait")
        mci('close music')


class duThread(QThread):   # TTS线程
    def __init__(self, parent, tex, spd, pit, vol, speaker):
        super(duThread, self).__init__(parent)
        self.text = tex
        self.spd = spd
        self.pit = pit
        self.vol = vol
        self.speaker = speaker

    def run(self):
        APP_ID = "9858951"
        API_KEY = "dwVtSTfGRc0gL73MfaFIWTKe"
        SECRET_KEY = "AhRU0ueWfxCGtUlHyVe5AtzZh6r16W26"
        aipSpeak = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
        result = aipSpeak.synthesis(self.text, 'zh', 1, {'spd': self.spd,
                                                         'pit': self.pit,
                                                         'vol': self.vol,
                                                         'per': self.speaker
                                                         }
                                    )
        if not isinstance(result, dict):
            with open('audio.mp3', 'wb') as f:
                f.write(result)
        else:
            print result


class duPicTread(QThread):   # 图片识别线程
    signal_picText = pyqtSignal(str)  # 信号

    def __init__(self, parent=None):
        super(duPicTread, self).__init__(parent)
        self.path = None

    def setPicPath(self, path):
        self.path = path
        self.start()

    def run(self):
        APP_ID = "9858951"
        API_KEY = "dwVtSTfGRc0gL73MfaFIWTKe"
        SECRET_KEY = "AhRU0ueWfxCGtUlHyVe5AtzZh6r16W26"
        aipOcr = AipOcr(APP_ID, API_KEY, SECRET_KEY)
        im = Image.open(self.path)
        im = im.convert('RGB')
        im.save('image.jpg', 'jpeg')

        def get_file_content(path):   # 读取图片
            with open(path, 'rb') as fp:
                return fp.read()

        result = aipOcr.webImage(get_file_content('image.jpg'))  # 网络图片文字文字识别接口
        print result
        r = []
        for res in result['words_result']:
            tex = res['words']
            r.append(tex)
        strRes = "".join(r)
        self.signal_picText.emit(strRes)


class duApp(QMainWindow):
    def __init__(self):
        QWidget.__init__(self)
        self.ui = Ui_du_Ui()
        self.ui.setupUi(self)
        self.addClipBordListener()
        self.ui.pushButton.clicked.connect(self.play)
        self.ui.pushButton_3.clicked.connect(self.reTTS)
        self.connect(self.ui.horizontalSlider,
                     QtCore.SIGNAL('valueChanged(int)'),
                     self.changeValue)
        self.connect(self.ui.horizontalSlider_2,
                     QtCore.SIGNAL('valueChanged(int)'),
                     self.changeValue)
        self.connect(self.ui.horizontalSlider_3,
                     QtCore.SIGNAL('valueChanged(int)'),
                     self.changeValue)

    def addClipBordListener(self):
        cb = QApplication.clipboard()
        cb.dataChanged.connect(self.tt)

    def changeValue(self):
        spd = self.ui.horizontalSlider.value()
        pit = self.ui.horizontalSlider_2.value()
        vol = self.ui.horizontalSlider_3.value()
        self.ui.label_8.setText(QtCore.QString(str(spd)))
        self.ui.label_9.setText(QtCore.QString(str(pit)))
        self.ui.label_10.setText(QtCore.QString(str(vol)))

    def play(self):
        self.mciTread = mciThread(self, 'audio.mp3')
        self.mciTread.start()

    def reTTS(self):
        self.tt()

    def outPath(self, text):
        tex = unicode(text)
        print tex
        spd = self.ui.horizontalSlider.value()
        pit = self.ui.horizontalSlider_2.value()
        vol = self.ui.horizontalSlider_3.value()
        speaker = self.ui.comboBox.currentIndex()
        if tex != "":
            r = QtCore.QStringList([])
            for ct in tex:
                py = slug(ct, style=pypinyin.TONE, errors='ignore')
                if py != '':
                    dp = ct + '(' + py + ')'
                else:
                    dp = ct
                r.append(dp)
            et = r.join("")
            self.ui.textEdit.setText(QtCore.QString(et))
            self.ui.lineEdit.setText(tex)
            self.duTts = duThread(self, tex, spd, pit, vol, speaker)
            self.duTts.finished.connect(self.play)
            self.duTts.start()

    def tt(self):
        cb = QApplication.clipboard()
        data = cb.mimeData()
        if data.hasUrls() or data.hasImage():
            self.ui.toolBox.setCurrentIndex(1)
            for url in data.urls():
                filePath = unicode(url.toLocalFile())
                print(filePath)
                image = QImage(filePath)
                pix = QPixmap.fromImage(image)
                self.ui.label_2.setPixmap(
                    pix.scaled(
                        self.ui.label_2.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                )
                self.duPic = duPicTread()
                self.duPic.setPicPath(filePath)
                self.duPic.signal_picText.connect(self.outPath)

        elif data.hasText():
            self.ui.toolBox.setCurrentIndex(0)
            tex = data.text()
            self.outPath(tex)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = duApp()
    app.setActiveWindow(w)
    w.show()
    app.exec_()
