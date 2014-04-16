#coding: utf-8
import wx
import threading
import os
import settings
import lib.util as util
from media_repo import MediaRepo

def add_file(src_path, file_meta):
    repo = MediaRepo()
    repo.add_bookinfo(file_meta)
    repo.add_history(file_meta['md5'], src_path)
    return 1



class FileScan(threading.Thread):

    def __init__(self, tar_path, window):
        threading.Thread.__init__(self)
        self.stopFlag = False
        self.ignore_seq = settings.ignore_seq or set()
        self.ignore_hidden = settings.ignore_hidden
        self.ext_pool = settings.ext_pool

        self.file_hdlr = add_file
        self.tar_path = tar_path 
        self.window = window
        self.cnt_scanned = 0

    def stop(self):
        self.stopFlag = True

    def run(self):
        cnt_found = self.scan_path(self.tar_path)
        wx.CallAfter(self.window.scan_stopped, self.tar_path, cnt_found, self.cnt_scanned)

    def scan_path(self, src_path):
        """scan path to detect target files

        @src_path: unicode encoding is required"""
        if not os.path.exists(src_path):  # not exists
            return None

        if os.path.isfile(src_path):  # file
            rawname, ext = os.path.splitext(os.path.basename(src_path))
            if not ext or ext not in self.ext_pool:  # file extension check
                return 0
            file_meta = {'rawname': [rawname],
                         'ext': ext,
                         'md5': util.md5_for_file(src_path),
                         }
            wx.CallAfter(self.window.file_found, src_path, file_meta['md5'])
            return self.file_hdlr(src_path, file_meta) or 0
        else:  # dir
            added = 0
            # ignore log/.git etc
            tar_path = set(os.listdir(src_path)) - self.ignore_seq
            self.cnt_scanned += len(tar_path)
            wx.CallAfter(self.window.file_scanned, self.cnt_scanned)
            for rel_path in tar_path:
                if self.stopFlag:
                    return added
                abs_path = os.path.join(src_path, rel_path)
                if self.ignore_hidden and util.is_hiden(abs_path):
                    continue  # ignore hidden
                else:
                    added += self.scan_path(abs_path) or 0
            return added


class ScanFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="Scan Books",
                          pos=(100, 100), size=(1180, 600))
        self.threads = []
        self.buildUI()

    def buildUI(self):
        frameStyle = wx.TE_AUTO_SCROLL | wx.TE_MULTILINE
        self.scan_log = wx.TextCtrl(parent=self, style=frameStyle)
        self.scan_log.SetEditable(False)

        # toolbox
        self.startBtn = wx.Button(parent=self, label="Start")
        self.stopBtn = wx.Button(parent=self, label="Stop")
        self.startBtn.Enable()
        self.stopBtn.Disable()
        self.scan_cnt_label = wx.StaticText(parent=self, label='Files Scanned:', style=wx.ALIGN_CENTER)
        self.scan_cnt_value = wx.StaticText(parent=self, label='0', style=wx.ALIGN_CENTER)

        self.toolbox = wx.BoxSizer(wx.VERTICAL)
        self.toolbox.Add(self.startBtn, 1, wx.ALL | wx.EXPAND, 5, 0)
        self.toolbox.Add(self.stopBtn, 1, wx.ALL | wx.EXPAND, 5, 0)
        self.toolbox.Add(self.scan_cnt_label, 1, wx.ALL | wx.EXPAND, 5, 0)
        self.toolbox.Add(self.scan_cnt_value, 1, wx.ALIGN_CENTER, 5, 0)
        
        self.mainbox = wx.BoxSizer(wx.HORIZONTAL)
        self.mainbox.Add(self.scan_log, 1, wx.ALL | wx.EXPAND, 5, 5)
        self.mainbox.Add(self.toolbox, 0, wx.NORMAL, 0, 0)

        self.SetSizer(self.mainbox)
        self.CenterOnScreen()

        self.startBtn.Bind(wx.EVT_BUTTON, self.OnStartScan)
        self.stopBtn.Bind(wx.EVT_BUTTON, self.OnStopScan)

    def file_found(self, filepath, md5):
        self.scan_log.AppendText('add %s, md5: %s\n' % (filepath, md5))

    def file_scanned(self, cnt):
        self.scan_cnt_value.SetLabel(str(cnt))

    def scan_stopped(self, scanned_path, cnt_found, cnt_scanned):
        self.startBtn.Enable()
        self.stopBtn.Disable()
        msg = '\nscan finished! %s/%s (found/scanned) in %s\n'\
                % (cnt_found, cnt_scanned, os.path.abspath(scanned_path))
        self.scan_log.AppendText(msg)

    def OnStartScan(self, event):
        # clear log if too big
        if len(self.scan_log.GetValue()) > 1024:
            self.scan_log.SetValue('')
        dlg = wx.DirDialog(self, "Choose a directory:")
        if dlg.ShowModal() == wx.ID_OK:
            self.startBtn.Disable()
            self.stopBtn.Enable()
            scan_thread = FileScan(dlg.GetPath(), self)
            self.threads.append(scan_thread)
            scan_thread.start()

    def OnStopScan(self, event):
        while self.threads:
            thread = self.threads[0]
            thread.stop()
            self.threads.remove(thread)


class TestApp(wx.App):

    def OnInit(self):
        frame = ScanFrame()
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

if __name__ == "__main__":
    app = TestApp()
    app.MainLoop()
