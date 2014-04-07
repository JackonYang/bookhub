#coding: utf-8
import wx
from file_repo import FileRepo


class ScanFrame(wx.Frame):

    def __init__(self, db):
        wx.Frame.__init__(self, parent=None, title="Scan Books",
                          pos=(100, 100), size=(1180, 600))
        self.buildUI()
        self.CenterOnScreen()
        self.repo = FileRepo(db, self._out_scan, self._out_debug)

    def buildUI(self):
        self.box1 = wx.BoxSizer(wx.HORIZONTAL)
        frameStyle = wx.TE_AUTO_SCROLL | wx.TE_MULTILINE
        self.text = wx.TextCtrl(parent=self, style=frameStyle)
        self.text.SetEditable(False)
        self.box1.Add(self.text, 1, wx.ALL | wx.EXPAND, 5, 5)

        self.toolbox = wx.BoxSizer(wx.VERTICAL)
        self.startBtn = wx.Button(parent=self, label="Start")
        self.toolbox.Add(self.startBtn, 1, wx.ALL | wx.EXPAND, 5, 0)
        self.stopBtn = wx.Button(parent=self, label="Stop")
        self.toolbox.Add(self.stopBtn, 1, wx.ALL | wx.EXPAND, 5, 0)
        self.box1.Add(self.toolbox, 0, wx.NORMAL, 0, 0)
        self.startBtn.Enable()
        self.stopBtn.Disable()

        self.SetSizer(self.box1)

        self.startBtn.Bind(wx.EVT_BUTTON, self.OnStartScan)
        self.stopBtn.Bind(wx.EVT_BUTTON, self.OnStopScan)

    def _out_scan(self, cnt):
        pass
        #print '%s files scanned' % cnt

    def _out_debug(self, msg):
        self.text.AppendText(msg + '\n')

    def OnStartScan(self, event):
        self.startBtn.Disable()
        self.stopBtn.Enable()
        # clear log if too big
        if len(self.text.GetValue()) > 1024:
            self.text.SetValue('')
        dlg = wx.DirDialog(self, "Choose a directory:")
        if dlg.ShowModal() == wx.ID_OK:
            wx.CallAfter(self.repo.add_books, dlg.GetPath())

    def OnStopScan(self, event):
        pass


class TestApp(wx.App):

    def OnInit(self):

        from settings import db_host, db_port, db_name
        from lib.mongo_hdlr import MongodbHandler
        mongo = MongodbHandler()
        mongo.connect(db_host, db_port)
        db = mongo.get_db(db_name)
        frame = ScanFrame(db)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

if __name__ == "__main__":
    app = TestApp()
    app.MainLoop()
