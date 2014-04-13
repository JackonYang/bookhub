# -*- coding: utf-8 -*-
"""
Required: MediaRepo
+get_booklist()
+open_book(BookMetaObj)

"""
import wx
from lib.ObjectListView import ObjectListView, ColumnDefn
from lib.ObjectListView import Filter
import lib.util as util
import subprocess

showlist = ['title', 'language', 'size', 'md5']
cols = {'title': ColumnDefn("Title", "left", 330, "get_dispname", stringConverter='%s', valueSetter='set_dispname'),
        'language': ColumnDefn("Language", "center", 80, "get_book_language", stringConverter='%s', isEditable=False),
        'size': ColumnDefn("Size", "right", 80, "getSizeString", stringConverter='%s', isEditable=False),
        'md5': ColumnDefn("MD5", "center", 320, "md5", stringConverter='%s', isEditable=False),
        }

class OverViewFrame(wx.Frame):
    def __init__(self, repo):
        FrameStyle = wx.CAPTION | wx.RESIZE_BORDER | wx.SYSTEM_MENU |\
            wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.CLOSE_BOX
        wx.Frame.__init__(self, parent=None, id=-1, title="BookHub",
                          pos=(100, 100), size=(500, 600), style=FrameStyle)

        self.BuildUI()
        self.InitObjectListView(repo)
        self.InitSearchCtrls()

    def BuildUI(self):
        self.SearchFile = wx.SearchCtrl(self)
        self.myOlv = ObjectListView(self, -1,
                                    style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        size_main = wx.BoxSizer(wx.VERTICAL)
        size_main.Add(self.SearchFile, 1, wx.ALL | wx.EXPAND, 2)
        size_main.Add(self.myOlv, 20, wx.ALL | wx.EXPAND, 4)
        self.SetSizer(size_main)
        self.Layout()
        self.CenterOnScreen()

        self.myOlv.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnOpenFile)
        self.myOlv.Bind(wx.EVT_LIST_KEY_DOWN, self.OnKeyDown)

    def InitObjectListView(self, repo):
        self.repo = repo
        self.myOlv.SetColumns([cols[k.lower()] for k in showlist])
        self.myOlv.SetObjects(self.repo.get_booklist())
        self.myOlv.cellEditMode = ObjectListView.CELLEDIT_SINGLECLICK

    def InitSearchCtrls(self):
        """Initialize the search controls"""
        for (searchCtrl, olv) in [(self.SearchFile, self.myOlv)]:

            def _handleText(evt, searchCtrl=searchCtrl, olv=olv):
                self.OnTextSearchCtrl(evt, searchCtrl, olv)

            def _handleCancel(evt, searchCtrl=searchCtrl, olv=olv):
                self.OnCancelSearchCtrl(evt, searchCtrl, olv)

            searchCtrl.Bind(wx.EVT_TEXT, _handleText)
            searchCtrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, _handleCancel)
            searchCtrl.SetFocus()
            olv.SetFilter(Filter.TextSearch(olv, olv.columns[0:4]))

    def OnOpenFile(self, event):
        obj = self.myOlv.GetSelectedObject()
        path = self.repo.getFilePath(obj)
        if path is None:
            wx.MessageBox('File not exists', 'Bookhub Message')
            return
        cmd = util.cmd_open_file(path)
        res = subprocess.call(cmd, shell=True)
        if res != 0:
            wx.MessageBox('Open File Error. returncode %s' % res, 'Bookhub Message')

    def OnKeyDown(self, event):
        objs = self.myOlv.GetSelectedObjects()
        key = event.GetKeyCode()
        if wx.WXK_DELETE == key:
            self.DoDelete(objs)
        elif 3 == key:  # wx.WXK_CONTROL_C
            self.DoCopyFileid(objs)

    def DoDelete(self, objs):
        for obj in objs:
            pass
            # obj.delete()
        self.myOlv.RemoveObjects(objs)

    def DoCopyFileid(self, objs):
        self.dataObj = wx.TextDataObject()
        file_ids = ','.join([obj.file_id for obj in objs])
        wx.MessageBox(file_ids, "MD5 code")
        # self.dataObj.SetText(file_ids)
        # if wx.TheClipboard.Open():
        #   wx.TheClipboard.SetData(self.dataObj)
        #    wx.TheClipboard.Close()
        #else:
        #    wx.MessageBox("Unable to open the clipboard", "Error")

    def OnTextSearchCtrl(self, event, searchCtrl, olv):
        searchCtrl.ShowCancelButton(len(searchCtrl.GetValue()))
        olv.GetFilter().SetText(searchCtrl.GetValue())
        olv.RepopulateList()

    def OnCancelSearchCtrl(self, event, searchCtrl, olv):
        searchCtrl.SetValue("")
        self.OnTextSearchCtrl(event, searchCtrl, olv)


class TestApp(wx.App):

    def OnInit(self):
        from media_repo import MediaRepo
        repo = MediaRepo()
        frame = OverViewFrame(repo)
        self.SetTopWindow(frame)
        frame.Show()
        return True


if __name__ == '__main__':
    app = TestApp()
    app.MainLoop()
