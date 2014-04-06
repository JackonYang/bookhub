# -*- coding: utf-8 -*-
#!/usr/bin/python
import wx


def LabelText(label, default_value, parent=None):
    return (wx.StaticText(parent, label=label),  # Label
            wx.TextCtrl(parent, size=(150, -1),  # Panel
                        value=default_value, style=wx.TE_PROCESS_ENTER)
            )


class ConnectDialog(wx.Dialog):

    def __init__(self, db, parent=None):
        wx.Dialog.__init__(self, parent=parent, id=-1)

        self.db = db  # db handler. connect() method is required
        self.SetTitle("Connect Mongo")

        # widgets
        labelHost, self.inputHost = LabelText('Host: ', 'localhost', self)
        labelPort, self.inputPort = LabelText('Port: ', '27017', self)
        btnConn = wx.Button(self, label='Connect')
        btnCancel = wx.Button(self, id=wx.ID_CANCEL, label="Cancel")

        # event handler
        self.Bind(wx.EVT_BUTTON, self.OnConnect, btnConn)
        # connet if user press enter
        self.Bind(wx.EVT_TEXT_ENTER, self.OnConnect, self.inputHost)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnConnect, self.inputPort)

        # default settings
        self.inputHost.SetFocus()

        # Layout-inputs
        gridInputs = wx.FlexGridSizer(2, 2, 10, 10)
        gridInputs.SetFlexibleDirection = wx.HORIZONTAL
        gridInputs.AddMany([(labelHost), (self.inputHost, 0, wx.EXPAND),
                            (labelPort), (self.inputPort, 0, wx.EXPAND),
                            ])
        # Layout-action button
        sizer_act = wx.BoxSizer(wx.HORIZONTAL)
        sizer_act.Add(btnConn, 1, wx.ALIGN_CENTER | wx.FIXED_MINSIZE, 10)
        sizer_act.Add(btnCancel, 1, wx.ALIGN_CENTER | wx.FIXED_MINSIZE, 10)
        # main sizer
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_main.Add(gridInputs, 2, flag=wx.ALL | wx.EXPAND, border=10)
        sizer_main.Add(sizer_act, 1, wx.ALIGN_CENTER | wx.FIXED_MINSIZE, 10)
        self.SetSizer(sizer_main)
        self.SetAutoLayout(1)
        sizer_main.Fit(self)

    def OnConnect(self, event=None):
        host = self.inputHost.GetValue()
        port = int(self.inputPort.GetValue())
        if db.connect(host, port):
            self.EndModal(wx.ID_OK)
        else:
            msg_error = 'Error connecting to host(%s)' % host
            wx.MessageBox(msg_error, 'Error', wx.OK | wx.ICON_ERROR)


class TestApp(wx.App):

    def OnInit(self):
        dlg = ConnectDialog(db, parent=None)
        res = dlg.ShowModal()
        if res == wx.ID_OK:
            print 'Connected'
        else:
            print 'Unconnect'
        dlg.Destroy()
        return True


if __name__ == '__main__':
    from lib.mongo_hdlr import MongodbHandler
    db = MongodbHandler()
    app = TestApp()
