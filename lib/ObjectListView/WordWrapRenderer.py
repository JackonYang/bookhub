# -*- coding: utf-8 -*-
#!/usr/bin/env python
#----------------------------------------------------------------------------
# Name:         WordWrapRenderer.py
# Author:       Phillip Piper
# Created:      25 July 2008
# SVN-ID:       $Id$
# Copyright:    (c) 2008 by Phillip Piper, 2008
# License:      wxWindows license
#----------------------------------------------------------------------------
# Change log:
# 2008/07/25  JPP   Initial version
#----------------------------------------------------------------------------
# To do:

"""
A WordWrapRenderer encapsulates the ability to draw and measure word wrapped
strings directly to a device context.

It is meant to be good enough for general use. It is not suitable for typographic layout
-- it does not handle kerning or ligatures.

The DC passed to these methods cannot be a GraphicContext DC. These methods use
GetPartialTextExtents() which does not work with GCDC's (as of wx 2.8).

"""

import wx
import bisect
from wx.lib.wordwrap import wordwrap

class WordWrapRenderer:
    """
    This renderer encapsulates the logic need to draw and measure a word-wrapped
    string within a given rectangle.
    """

    #----------------------------------------------------------------------------
    # Calculating

    @staticmethod
    def CalculateHeight(dc, text, width):
        """
        Calculate the height of the given text when fitted within the given width.

        Remember to set the font on the dc before calling this method.
        """
        # There is a bug in the wordwrap routine where a string that needs truncated and
        # that ends with a single space causes the method to throw an error (wx 2.8).
        # Our simple, but not always accurate, is to remove trailing spaces.
        # This won't catch single trailing space imbedded in a multiline string.
        text = text.rstrip(' ')

        lines = wordwrap(text, width, dc, True)
        (width, height, descent, externalLeading) = dc.GetFullTextExtent("Wy")
        return (lines.count("\n")+1) * (height + externalLeading)


    #----------------------------------------------------------------------------
    # Rendering

    @staticmethod
    def DrawString(dc, text, bounds, align=wx.ALIGN_LEFT, valign=wx.ALIGN_TOP, allowClipping=False):
        """
        Draw the given text word-wrapped within the given bounds.

        bounds must be a wx.Rect or a 4-element collection: (left, top, width, height).

        If allowClipping is True, this method changes the clipping region so that no
        text is drawn outside of the given bounds.
        """
        if not text:
            return

        if align == wx.ALIGN_CENTER:
            align = wx.ALIGN_CENTER_HORIZONTAL

        if valign == wx.ALIGN_CENTER:
            valign = wx.ALIGN_CENTER_VERTICAL

        # DrawLabel only accepts a wx.Rect
        try:
            bounds = wx.Rect(*bounds)
        except:
            pass

        if allowClipping:
            clipper = wx.DCClipper(dc, bounds)

        # There is a bug in the wordwrap routine where a string that needs truncated and
        # that ends with a single space causes the method to throw an error (wx 2.8).
        # Our simple, but not always accurate, is to remove trailing spaces.
        # This won't catch single trailing space imbedded in a multiline string.
        text = text.rstrip(' ')

        lines = wordwrap(text, bounds[2], dc, True)
        dc.DrawLabel(lines, bounds, align|valign)


    @staticmethod
    def DrawTruncatedString(dc, text, bounds, align=wx.ALIGN_LEFT, valign=wx.ALIGN_TOP, ellipse=wx.RIGHT, ellipseChars="..."):
        """
        Draw the given text truncated to the given bounds.

        bounds must be a wx.Rect or a 4-element collection: (left, top, width, height).

        If allowClipping is True, this method changes the clipping region so that no
        text is drawn outside of the given bounds.
        """
        if not text:
            return

        if align == wx.ALIGN_CENTER:
            align = wx.ALIGN_CENTER_HORIZONTAL

        if valign == wx.ALIGN_CENTER:
            valign = wx.ALIGN_CENTER_VERTICAL

        try:
            bounds = wx.Rect(*bounds)
        except:
            pass
        lines = WordWrapRenderer._Truncate(dc, text, bounds[2], ellipse, ellipseChars)
        dc.DrawLabel(lines, bounds, align|valign)


    @staticmethod
    def _Truncate(dc, text, maxWidth, ellipse, ellipseChars):
        """
        Return a string that will fit within the given width.
        """
        line = text.split("\n")[0] # only consider the first line
        if not line:
            return ""

        pte = dc.GetPartialTextExtents(line)

        # Does the whole thing fit within our given width?
        stringWidth = pte[-1]
        if stringWidth <= maxWidth:
            return line

        # We (probably) have to ellipse the text so allow for ellipse
        maxWidthMinusEllipse = maxWidth - dc.GetTextExtent(ellipseChars)[0]

        if ellipse == wx.LEFT:
            i = bisect.bisect(pte, stringWidth - maxWidthMinusEllipse)
            return ellipseChars + line[i+1:]

        if ellipse == wx.CENTER:
            i = bisect.bisect(pte, maxWidthMinusEllipse / 2)
            j = bisect.bisect(pte, stringWidth - maxWidthMinusEllipse / 2)
            return line[:i] + ellipseChars + line[j+1:]

        if ellipse == wx.RIGHT:
            i = bisect.bisect(pte, maxWidthMinusEllipse)
            return line[:i] + ellipseChars

        # No ellipsing, just truncating is the default
        i = bisect.bisect(pte, maxWidth)
        return line[:i]

#======================================================================
# TESTING ONLY
#======================================================================

if __name__ == '__main__':

    class TestPanel(wx.Panel):
        def __init__(self, parent):
            wx.Panel.__init__(self, parent, -1, style=wx.FULL_REPAINT_ON_RESIZE)
            self.Bind(wx.EVT_PAINT, self.OnPaint)

            self.text = """This is Thisisareallylongwordtoseewhathappens the text to be drawn. It needs to be long to see if wrapping works.  to long words.
This is on new line by itself.

This should have a blank line in front of it but still wrap when we reach the edge.

The bottom of the red rectangle should be immediately below this."""
            self.font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, faceName="Gill Sans")

        def OnPaint(self, evt):
            dc = wx.PaintDC(self)
            inset = (20, 20, 20, 20)
            rect = [inset[0], inset[1], self.GetSize().width-(inset[0]+inset[2]), self.GetSize().height-(inset[1]+inset[3])]

            # Calculate exactly how high the wrapped is going to be and put a frame around it.
            dc.SetFont(self.font)
            dc.SetPen(wx.RED_PEN)
            rect[3] = WordWrapRenderer.CalculateHeight(dc, self.text, rect[2])
            dc.DrawRectangle(*rect)
            WordWrapRenderer.DrawString(dc, self.text, rect, wx.ALIGN_LEFT)
            #WordWrapRenderer.DrawTruncatedString(dc, self.text, rect, wx.ALIGN_CENTER_HORIZONTAL,s ellipse=wx.CENTER)

            #bmp = wx.EmptyBitmap(rect[0]+rect[2], rect[1]+rect[3])
            #mdc = wx.MemoryDC(bmp)
            #mdc.SetBackground(wx.Brush("white"))
            #mdc.Clear()
            #mdc.SetFont(self.font)
            #mdc.SetPen(wx.RED_PEN)
            #rect[3] = WordWrapRenderer.CalculateHeight(mdc, self.text, rect[2])
            #mdc.DrawRectangle(*rect)
            #WordWrapRenderer.DrawString(mdc, self.text, rect, wx.ALIGN_LEFT)
            #del mdc
            #dc = wx.ScreenDC()
            #dc.DrawBitmap(bmp, 20, 20)

    class MyFrame(wx.Frame):
        def __init__(self, *args, **kwds):
            kwds["style"] = wx.DEFAULT_FRAME_STYLE
            wx.Frame.__init__(self, *args, **kwds)

            self.panel = wx.Panel(self, -1)
            self.testPanel = TestPanel(self.panel)

            sizer_2 = wx.BoxSizer(wx.VERTICAL)
            sizer_2.Add(self.testPanel, 1, wx.ALL|wx.EXPAND, 4)
            self.panel.SetSizer(sizer_2)
            self.panel.Layout()

            sizer_1 = wx.BoxSizer(wx.VERTICAL)
            sizer_1.Add(self.panel, 1, wx.EXPAND)
            self.SetSizer(sizer_1)
            self.Layout()


    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
