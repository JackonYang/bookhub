# -*- coding: utf-8 -*-
#!/usr/bin/env python
#----------------------------------------------------------------------------
# Name:         ListCtrlPrinter.py
# Author:       Phillip Piper
# Created:      17 July 2008
# SVN-ID:       $Id$
# Copyright:    (c) 2008 by Phillip Piper, 2008
# License:      wxWindows license
#----------------------------------------------------------------------------
# Change log:
# 2008/07/17  JPP   Inspired beginning
#----------------------------------------------------------------------------
# To do:
# - persistence of ReportFormat
# - allow cell contents to be vertically aligned
# - in light of several of the "to dos", consider having CellBlockFormat object
# - write a data abstraction layer between the printer and the ListCtrl.
#   This layer could understand ObjectListViews and be more efficient.
# - consider if this could be made to work with a wx.Grid (needs data abstraction layer)

# Known issues:
# - the 'space' setting on decorations is not intuitive


"""
An ``ListCtrlPrinter`` takes an ``ObjectListView`` or ``wx.ListCtrl`` and turns it into a
pretty report.

As always, the goal is for this to be as easy to use as possible. A typical
usage should be as simple as::

   printer = ListCtrlPrinter(self.myOlv, "My Report Title")
   printer.PrintPreview()

This will produce a report with reasonable formatting. The formatting of a report is
controlled completely by the ReportFormat object of the ListCtrlPrinter. To change the appearance
of the report, you change the settings in this object.

A report consists of various sections (called "blocks") and each of these blocks has a
matching BlockFormat object in the ReportFormat. So, to modify the format of the
page header, you change the ReportFormat.PageHeader object.

A ReportFormat object has the following properties which control the appearance of the matching
sections of the report:

* PageHeader
* ListHeader
* ColumnHeader
* GroupTitle
* Row
* ListFooter
* PageFooter
* Page

These properties return BlockFormat objects, which have the following properties:

* AlwaysCenter
* CanWrap
* Font
* Padding
* TextAlignment
* TextColor

* CellPadding
* GridPen

Implementation
==============

A ``ListCtrlPrinter`` is a *Facade* over two classes:
    - ``ListCtrlPrintout``, which handles the interface to the wx printing subsystem
    - ``ReportEngine``, which does the actual work of creating the report

The ``ListCtrlPrintout`` handles all the details of the wx printing subsystem. In
particular, it configures the printing DC so that its origin and scale are correct. This
enables the ``ReportEngine`` to simply render the report without knowing the
characteristics of the underlying printer DPI, unprintable region, or the scale of a print
preview. When The ``ListCtrlPrintout`` encounters some action that is cannot perform (like
actually rendering a page) it calls back into ``ListCtrlPrinter`` (which simply forwards
to the ``ReportEngine``).

The ``ReportEngine`` uses a block structure approach to reports. Each element of
a report is a "block", which stacks vertically with other blocks.

When a block is printed, it can either render itself into a given DC or it can replace
itself in the report structure with one or more other blocks. A ``TextBlock`` renders
itself by drawing into the DC. In contrast, the block that prints a ``ListCtrl`` replaces
itself with a ``ListHeaderBlock``, a ``ColumnHeaderBlock``, ``ListRowsBlock`` and finally a
``ListFooterBlock``.

The blocks describe the structure of the report. The formatting of a report is
controlled by ``BlockFormat`` objects. The ``ReportFormat`` contains a ``BlockFormat``
object for each formattable section of the report.

Each section must be formatted in same fashion, i.e. all column headers will look the same,
all page footer will look the same. There is no way to make the first footer look one way,
and the second look a different way.
"""

import datetime
import math

import wx

from WordWrapRenderer import WordWrapRenderer

#----------------------------------------------------------------------------

class ListCtrlPrinter(object):
    """
    An ListCtrlPrinter creates a pretty report from an ObjectListView/ListCtrl.

    """

    def __init__(self, listCtrl=None, title="ListCtrl Printing"):
        """
        """
        self.printout = ListCtrlPrintout(self)
        self.engine = ReportEngine()
        if listCtrl is not None:
            self.AddListCtrl(listCtrl, title)

    #----------------------------------------------------------------------------
    # Accessing

    def GetPageFooter(self):
        """
        Return a 3-tuple of the texts that will be shown in left, center, and right cells
        of the page footer
        """
        return self.engine.pageFooter

    def SetPageFooter(self, leftText="", centerText="", rightText=""):
        """
        Set the texts that will be shown in various cells of the page footer.

        leftText can be a string or a 3-tuple of strings.
        """
        if isinstance(leftText, (tuple, list)):
            self.engine.pageFooter = leftText
        else:
            self.engine.pageFooter = (leftText, centerText, rightText)

    def GetPageHeader(self):
        """
        Return a 3-tuple of the texts that will be shown in left, center, and right cells
        of the page header
        """
        return self.engine.pageHeader

    def SetPageHeader(self, leftText="", centerText="", rightText=""):
        """
        Set the texts that will be shown in various cells of the page header
        """
        if isinstance(leftText, (tuple, list)):
            self.engine.pageHeader = leftText
        else:
            self.engine.pageHeader = (leftText, centerText, rightText)

    def GetPrintData(self):
        """
        Return the wx.PrintData that controls the printing of this report
        """
        return self.printout.printData

    def GetReportFormat(self):
        """
        Return the ReportFormat object that controls the appearance of this printout
        """
        return self.engine.reportFormat

    def SetReportFormat(self, fmt):
        """
        Set the ReportFormat object that controls the appearance of this printout
        """
        self.engine.reportFormat = fmt

    def GetWatermark(self, txt):
        """
        Get the text that will be printed as a watermark on the report
        """
        return self.engine.watermark

    def SetWatermark(self, txt):
        """
        Set the text that will be printed as a watermark on the report
        """
        self.engine.watermark = txt

    ReportFormat = property(GetReportFormat, SetReportFormat)
    PageFooter = property(GetPageFooter, SetPageFooter)
    PageHeader = property(GetPageHeader, SetPageHeader)
    PrintData = property(GetPrintData)
    Watermark = property(GetWatermark, SetWatermark)

    #----------------------------------------------------------------------------
    # Setup

    def AddListCtrl(self, listCtrl, title=None):
        """
        Add the given list to those that will be printed by this report.
        """
        self.engine.AddListCtrl(listCtrl, title)


    def Clear(self):
        """
        Remove all ListCtrls from this printer
        """
        self.engine.ClearListCtrls()

    #----------------------------------------------------------------------------
    # Printing Commands

    def PageSetup(self, parent=None):
        """
        Show a Page Setup dialog that will change the configuration of this printout
        """
        self.printout.PageSetup(parent)


    def PrintPreview(self, parent=None, title="ListCtrl Print Preview", bounds=(20, 50, 800, 800)):
        """
        Show a Print Preview of this report
        """
        self.printout.PrintPreview(parent, title, bounds)


    def Print(self, parent=None):
        """
        Print this report to the selected printer
        """
        self.printout.DoPrint(parent)

    #----------------------------------------------------------------------------
    # Callbacks
    # These methods are invoked by the ListCtrlPrintout when required

    def CalculateTotalPages(self, dc, bounds):
        """
        Do the work of calculating how many pages this report will occupy?

        This is expensive because it basically prints the whole report.
        """
        return self.engine.CalculateTotalPages(dc, bounds)


    def StartPrinting(self):
        """
        A new print job is about to begin.
        """
        self.engine.StartPrinting()


    def PrintPage(self, dc, pageNumber, bounds):
        """
        Print the given page on the given device context.
        """
        self.engine.PrintPage(dc, pageNumber, bounds)

#----------------------------------------------------------------------------

class ReportEngine(object):
    """
    A ReportEngine handles all the work of actually producing a report.

    Public instance variables (all others should be treated as private):

    * dateFormat
         When the current date/time is substituted into report text, how should
         the datetime be formatted? This must be a valid format string for the
         strftime() method.
         Default: "%x %X"

    """

    def __init__(self):
        """
        """
        self.currentPage = -1
        self.totalPages = -1
        self.blocks = list()
        self.blockInsertionIndex = 0
        self.listCtrls = list()
        self.dateFormat = "%x %X"

        self.reportFormat = ReportFormat.Normal()

        self.watermark = ""
        self.pageHeader = list()
        self.pageFooter = list()
        #self.isPrintSelectionOnly = False # not currently implemented

        # If this is False, no drawing should be done. The engine is either counting
        # pages, or skipping to a specific page
        self.shouldDrawBlocks = True

    #----------------------------------------------------------------------------
    # Accessing

    def GetNamedFormat(self, name):
        """
        Return the given format
        """
        return self.reportFormat.GetNamedFormat(name)


    def GetTotalPages(self):
        """
        Return the total number of pages that this report will produce.

        CalculateTotalPages() must be called before this is accurate.
        """
        return self.totalPages


    def GetSubstitutionInfo(self):
        """
        Return a dictionary that can be used for substituting values into strings
        """
        dateString = datetime.datetime.now().strftime(self.dateFormat)
        info = {
            "currentPage": self.currentPage,
            "date": dateString,
            "totalPages": self.totalPages,
        }
        return info

    #----------------------------------------------------------------------------
    # Calculating

    def CalculateTotalPages(self, dc, bounds):
        """
        Do the work of calculating how many pages this report will occupy?

        This is expensive because it basically prints the whole report.
        """
        self.StartPrinting()
        self.totalPages = 1
        self.shouldDrawBlocks = False
        while self.PrintOnePage(dc, self.totalPages, bounds):
            self.totalPages += 1
        self.shouldDrawBlocks = True
        return self.totalPages

    #----------------------------------------------------------------------------
    # Commands

    def AddBlock(self, block):
        """
        Add the given block at the current insertion point
        """
        self.blocks.insert(self.blockInsertionIndex, block)
        self.blockInsertionIndex += 1
        block.engine = self


    def AddListCtrl(self, listCtrl, title=None):
        """
        Add the given list to those that will be printed by this report.
        """
        if listCtrl.InReportView():
            self.listCtrls.append([listCtrl, title])


    def ClearListCtrls(self):
        """
        Remove all ListCtrls from this report.
        """
        self.listCtrls = list()


    def DropCurrentBlock(self):
        """
        Remove the current block from our list of blocks
        """
        self.blocks.pop(0)
        self.blockInsertionIndex = 1

    #----------------------------------------------------------------------------
    # Printing

    def StartPrinting(self):
        """
        Initial a print job on this engine
        """
        self.currentPage = 0
        self.blockInsertionIndex = 0
        self.blocks = list()
        self.AddBlock(ReportBlock())
        self.runningBlocks = list()
        self.AddRunningBlock(PageHeaderBlock())
        self.AddRunningBlock(PageFooterBlock())

        if self.watermark:
            self._CreateReplaceWatermarkDecoration()


    def AddRunningBlock(self, block):
        """
        A running block is printed on every page until it is removed
        """
        self.runningBlocks.append(block)
        block.engine = self


    def RemoveRunningBlock(self, block):
        """
        A running block is printed on every page until it is removed
        """
        self.runningBlocks.remove(block)


    def PrintPage(self, dc, pageNumber, bounds):
        """
        Print the given page on the given device context.
        """
        # If the request page isn't next in order, we have to restart
        # the printing process and advance until we reach the desired page.
        if pageNumber != self.currentPage + 1:
            self.StartPrinting()
            self.shouldDrawBlocks = False
            for i in range(1, pageNumber):
                self.PrintOnePage(dc, i, bounds)
            self.shouldDrawBlocks = True

        return self.PrintOnePage(dc, pageNumber, bounds)


    def PrintOnePage(self, dc, pageNumber, bounds):
        """
        Print the current page on the given device context.

        Return true if there is still more to print.
        """
        # Initialize state
        self.currentPage = pageNumber
        self.pageBounds = list(bounds)
        self.workBounds = list(self.pageBounds)
        self.SubtractDecorations(dc)

        # Print page adornments, including under-text decorations
        self.DrawPageDecorations(dc, False)
        for x in self.runningBlocks:
            x.Print(dc)

        # Print blocks until they won't fit or we run out of blocks
        while len(self.blocks) and self.blocks[0].Print(dc):
            self.DropCurrentBlock()

        # Finally, print over-the-text decorations
        self.DrawPageDecorations(dc, True)

        return len(self.blocks) > 0


    def SubtractDecorations(self, dc):
        """
        # Subtract the area used from the work area
        """
        fmt = self.GetNamedFormat("Page")
        self.workBounds = fmt.SubtractDecorations(dc, self.workBounds)


    def DrawPageDecorations(self, dc, over):
        """
        Draw the page decorations
        """
        if not self.shouldDrawBlocks:
            return

        fmt = self.GetNamedFormat("Page")
        bounds = list(self.pageBounds)
        fmt.DrawDecorations(dc, bounds, self, over)


    def _CreateReplaceWatermarkDecoration(self):
        """
        Create a watermark decoration, replacing any existing watermark
        """
        pageFmt = self.GetNamedFormat("Page")
        pageFmt.decorations = [x for x in pageFmt.decorations if not isinstance(x, WatermarkDecoration)]

        watermarkFmt = self.GetNamedFormat("Watermark")
        pageFmt.Add(WatermarkDecoration(self.watermark, font=watermarkFmt.Font,
                                        color=watermarkFmt.TextColor, angle=watermarkFmt.Angle,
                                        over=watermarkFmt.Over))

#----------------------------------------------------------------------------

class ListCtrlPrintout(wx.Printout):
    """
    An ListCtrlPrintout is the interface between the wx printing system
    and ListCtrlPrinter.
    """

    def __init__(self, olvPrinter, margins=None):
        """
        """
        wx.Printout.__init__(self)
        self.olvPrinter = olvPrinter
        self.margins = margins or (wx.Point(15, 15), wx.Point(15, 15))
        self.totalPages = -1

        self.printData = wx.PrintData()
        self.printData.SetPrinterName("") # Use default printer
        self.printData.SetPaperId(wx.PAPER_A4)
        self.printData.SetPrintMode(wx.PRINT_MODE_PRINTER)


    #----------------------------------------------------------------------------
    # Accessing

    def HasPage(self, page):
        """
        Return true if this printout has the given page number
        """
        return page <= self.totalPages


    def GetPageInfo(self):
        """
        Return a 4-tuple indicating the ...
        """
        return (1, self.totalPages, 1, 1)


    def GetPrintPreview(self):
        """
        Get a wxPrintPreview of this report
        """
        data = wx.PrintDialogData(self.printData)
        forViewing = ListCtrlPrintout(self.olvPrinter, self.margins)
        forPrinter = ListCtrlPrintout(self.olvPrinter, self.margins)
        preview = wx.PrintPreview(forViewing, forPrinter, data)
        return preview

    #----------------------------------------------------------------------------
    # Commands

    def PageSetup(self, parent):
        """
        Show a Page Setup dialog that will change the configuration of this printout
        """
        data = wx.PageSetupDialogData()
        data.SetPrintData(self.printData)
        data.SetDefaultMinMargins(True)
        data.SetMarginTopLeft(self.margins[0])
        data.SetMarginBottomRight(self.margins[1])
        dlg = wx.PageSetupDialog(parent, data)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetPageSetupData()
            self.printData = wx.PrintData(data.GetPrintData())
            self.printData.SetPaperId(data.GetPaperId())
            self.margins = (data.GetMarginTopLeft(), data.GetMarginBottomRight())
        dlg.Destroy()



    def PrintPreview(self, parent, title, bounds):
        """
        Show a Print Preview of this report
        """
        self.preview = self.GetPrintPreview()

        if not self.preview.Ok():
            return False

        pfrm = wx.PreviewFrame(self.preview, parent, title)

        pfrm.Initialize()
        pfrm.SetPosition(bounds[0:2])
        pfrm.SetSize(bounds[2:4])
        pfrm.Show(True)

        return True


    def DoPrint(self, parent):
        """
        Send the report to the configured printer
        """
        try:
            pdd = wx.PrintDialogData(self.printData)
            printer = wx.Printer(pdd)

            if printer.Print(parent, self, True):
                self.printData = wx.PrintData(printer.GetPrintDialogData().GetPrintData())
            else:
                wx.MessageBox("There was a problem printing.\nPerhaps your current printer is not set correctly?", "Printing", wx.OK)
        finally:
            pdd.Destroy()


    #----------------------------------------------------------------------------
    # Event handlers

    def OnPreparePrinting(self):
        """
        Prepare for printing. This event is sent before any of the others
        """
        dc = self.GetDC()
        self.SetScaleAndBounds(dc)
        self.totalPages = self.olvPrinter.CalculateTotalPages(dc, self.bounds)
        self.olvPrinter.StartPrinting()

    def OnBeginDocument(self, start, end):
        """
        Begin printing one copy of the document. Return False to cancel the job
        """
        return super(ListCtrlPrintout, self).OnBeginDocument(start, end)

    def OnEndDocument(self):
        super(ListCtrlPrintout, self).OnEndDocument()

    def OnBeginPrinting(self):
        super(ListCtrlPrintout, self).OnBeginPrinting()

    def OnEndPrinting(self):
        super(ListCtrlPrintout, self).OnEndPrinting()

    def OnPrintPage(self, page):
        """
        Do the work of printing the given page number.
        """
        # We bounce this back to the printer facade
        dc = self.GetDC()
        self.SetScaleAndBounds(dc)
        return self.olvPrinter.PrintPage(dc, page, self.bounds)

    def SetScaleAndBounds(self, dc):
        """
        Calculate the scale required for our printout to match what appears on screen,
        and the bounds that will be effective at that scale and margins
        """
        # This code comes from Robin Dunn's "wxPython In Action."
        # Without that, I would never have figured this out.
        ppiPrinterX, ppiPrinterY = self.GetPPIPrinter()
        ppiScreenX, ppiScreenY = self.GetPPIScreen()
        logicalScale = float(ppiPrinterX) / float(ppiScreenX)
        pw, ph = self.GetPageSizePixels()
        dw, dh = dc.GetSize()
        scale = logicalScale * float(dw)/float(pw)
        dc.SetUserScale(scale, scale)

        # Now calculate our boundries
        logicalUnitsMM = float(ppiPrinterX) / (logicalScale*25.4)
        topLeft, bottomRight = self.margins
        left = round(topLeft.x * logicalUnitsMM)
        top = round(topLeft.y * logicalUnitsMM)
        right = round(dc.DeviceToLogicalYRel(dw) - bottomRight.x * logicalUnitsMM)
        bottom = round(dc.DeviceToLogicalYRel(dh) - bottomRight.y * logicalUnitsMM)
        self.bounds = (left, top, right-left, bottom-top)


#----------------------------------------------------------------------------

class ReportFormat(object):
    """
    A ReportFormat defines completely how a report is formatted.

    It holds a collection of BlockFormat objects which control the
    formatting of individual blocks of the report

    Public instance variables:

    * IncludeImages
        Should images from the ListCtrl be printed in the report?
        Default: *True*

    * IsColumnHeadingsOnEachPage
        Will the column headers be printed at the top of each page?
        Default: *True*

    * IsShrinkToFit
        Will the columns be shrunk so they all fit into the width of one page?
        Default: *False*

    * UseListCtrlTextFormat
        If this is True, the text format (i.e. font and text color) of each row will be taken from the ListCtrl,
        rather than from the *Cell* format.
        Default: *False*

    """

    def __init__(self):
        """
        """
        # Initialize the formats that control the various portions of the report
        self.Page = BlockFormat()
        self.PageHeader = BlockFormat()
        self.ListHeader = BlockFormat()
        self.GroupTitle = BlockFormat()
        self.ColumnHeader = BlockFormat()
        self.Row = BlockFormat()
        self.ListFooter = BlockFormat()
        self.PageFooter = BlockFormat()
        self.Watermark = BlockFormat()

        self.IncludeImages = True
        self.IsColumnHeadingsOnEachPage = False
        self.IsShrinkToFit = False
        self.UseListCtrlTextFormat = True

        # Initialize the watermark format to default values
        self.WatermarkFormat()

    #----------------------------------------------------------------------------
    # Accessing

    def GetNamedFormat(self, name):
        """
        Return the format used in to format a block with the given name.
        """
        return getattr(self, name)

    #----------------------------------------------------------------------------
    # Commands

    def WatermarkFormat(self, font=None, color=None, angle=30, over=False):
        """
        Change the format of the watermark printed on this report.

        The actual text of the water mark is set by `ListCtrlPrinter.Watermark` property.
        """
        defaultFaceName = "Stencil"
        self.Watermark.Font = font or wx.FFont(96, wx.FONTFAMILY_DEFAULT, 0, defaultFaceName)
        self.Watermark.TextColor = color or wx.Colour(204, 204, 204)
        self.Watermark.Angle = angle
        self.Watermark.Over = over

    #----------------------------------------------------------------------------
    # Standard formats
    # These are meant to be illustrative rather than definitive

    @staticmethod
    def Minimal(headerFontName="Arial", rowFontName="Times New Roman"):
        """
        Return a minimal format for a report
        """
        fmt = ReportFormat()
        fmt.IsShrinkToFit = False

        fmt.PageHeader.Font = wx.FFont(12, wx.FONTFAMILY_DEFAULT, face=headerFontName)
        fmt.PageHeader.Line(wx.BOTTOM, wx.BLACK, 1, space=5)
        fmt.PageHeader.Padding = (0, 0, 0, 12)

        fmt.ListHeader.Font = wx.FFont(18, wx.FONTFAMILY_DEFAULT, face=headerFontName)
        fmt.ListHeader.Padding = (0, 12, 0, 12)
        fmt.ListHeader.Line(wx.BOTTOM, wx.BLACK, 1, space=5)

        fmt.GroupTitle.Font = wx.FFont(12, wx.FONTFAMILY_DEFAULT, face=headerFontName)
        fmt.GroupTitle.Padding = (0, 12, 0, 12)
        fmt.GroupTitle.Line(wx.BOTTOM, wx.BLACK, 1, space=5)

        fmt.PageFooter.Font = wx.FFont(10, wx.FONTFAMILY_DEFAULT, face=headerFontName)
        fmt.PageFooter.Line(wx.TOP, wx.BLACK, 1, space=3)
        fmt.PageFooter.Padding = (0, 16, 0, 0)

        fmt.ColumnHeader.Font = wx.FFont(14, wx.FONTFAMILY_DEFAULT, wx.FONTFLAG_BOLD, face=headerFontName)
        fmt.ColumnHeader.Padding = (0, 12, 0, 12)
        fmt.ColumnHeader.CellPadding = 5
        fmt.ColumnHeader.Line(wx.BOTTOM, wx.Colour(192, 192, 192), 1, space=3)
        fmt.ColumnHeader.AlwaysCenter = True

        fmt.Row.Font = wx.FFont(10, wx.FONTFAMILY_DEFAULT, face=rowFontName)
        fmt.Row.CellPadding = 5
        fmt.Row.Line(wx.BOTTOM, wx.Colour(192, 192, 192), 1, space=3)
        fmt.Row.CanWrap = True

        return fmt

    @staticmethod
    def Normal(headerFontName="Gill Sans", rowFontName="Times New Roman"):
        """
        Return a reasonable default format for a report
        """
        fmt = ReportFormat()
        fmt.IsShrinkToFit = True

        fmt.PageHeader.Font = wx.FFont(12, wx.FONTFAMILY_DEFAULT, face=headerFontName)
        fmt.PageHeader.Line(wx.BOTTOM, wx.BLUE, 2, space=5)
        fmt.PageHeader.Padding = (0, 0, 0, 12)

        fmt.ListHeader.Font = wx.FFont(26, wx.FONTFAMILY_SWISS, wx.FONTFLAG_BOLD, face=headerFontName)
        fmt.ListHeader.TextColor = wx.WHITE
        fmt.ListHeader.Padding = (0, 12, 0, 12)
        fmt.ListHeader.TextAlignment = wx.ALIGN_LEFT
        fmt.ListHeader.Background(wx.BLUE, wx.WHITE, space=(16, 4, 0, 4))

        fmt.GroupTitle.Font = wx.FFont(14, wx.FONTFAMILY_DEFAULT, face=headerFontName)
        fmt.GroupTitle.Line(wx.BOTTOM, wx.BLUE, 4, toColor=wx.WHITE, space=5)
        fmt.GroupTitle.Padding = (0, 12, 0, 12)

        fmt.PageFooter.Font = wx.FFont(10, wx.FONTFAMILY_DEFAULT, face=headerFontName)
        fmt.PageFooter.Background(wx.WHITE, wx.BLUE, space=(0, 4, 0, 4))

        fmt.ColumnHeader.Font = wx.FFont(14, wx.FONTFAMILY_DEFAULT, wx.FONTFLAG_BOLD, face=headerFontName)
        fmt.ColumnHeader.CellPadding = 2
        fmt.ColumnHeader.Background(wx.Colour(192, 192, 192))
        fmt.ColumnHeader.GridPen = wx.Pen(wx.WHITE, 1)
        fmt.ColumnHeader.Padding = (0, 0, 0, 12)
        fmt.ColumnHeader.AlwaysCenter = True

        fmt.Row.Font = wx.FFont(12, wx.FONTFAMILY_DEFAULT, face=rowFontName)
        fmt.Row.Line(wx.BOTTOM, pen=wx.Pen(wx.BLUE, 1, wx.DOT), space=3)
        fmt.Row.CellPadding = 2
        fmt.Row.CanWrap = True

        return fmt

    @staticmethod
    def TooMuch(headerFontName="Chiller", rowFontName="Gill Sans"):
        """
        Return a reasonable default format for a report
        """
        fmt = ReportFormat()
        fmt.IsShrinkToFit = False

        fmt.PageHeader.Font = wx.FFont(12, wx.FONTFAMILY_DECORATIVE, wx.FONTFLAG_BOLD, face=headerFontName)
        fmt.PageHeader.TextColor = wx.WHITE
        fmt.PageHeader.Background(wx.GREEN, wx.RED, space=(16, 4, 0, 4))
        fmt.PageHeader.Padding = (0, 0, 0, 12)

        fmt.ListHeader.Font = wx.FFont(24, wx.FONTFAMILY_DECORATIVE, face=headerFontName)
        fmt.ListHeader.TextColor = wx.WHITE
        fmt.ListHeader.Padding = (0, 12, 0, 12)
        fmt.ListHeader.TextAlignment = wx.ALIGN_CENTER
        fmt.ListHeader.Background(wx.RED, wx.GREEN, space=(16, 4, 0, 4))

        fmt.GroupTitle.Font = wx.FFont(14, wx.FONTFAMILY_DECORATIVE, wx.FONTFLAG_BOLD, face=headerFontName)
        fmt.GroupTitle.TextColor = wx.BLUE
        fmt.GroupTitle.Padding = (0, 12, 0, 12)
        fmt.GroupTitle.Line(wx.BOTTOM, wx.GREEN, 4, toColor=wx.WHITE, space=5)

        fmt.PageFooter.Font = wx.FFont(10, wx.FONTFAMILY_DECORATIVE, face=headerFontName)
        fmt.PageFooter.Line(wx.TOP, wx.GREEN, 2, toColor=wx.RED, space=3)
        fmt.PageFooter.Padding = (0, 16, 0, 0)

        fmt.ColumnHeader.Font = wx.FFont(14, wx.FONTFAMILY_SWISS, wx.FONTFLAG_BOLD, face=headerFontName)
        fmt.ColumnHeader.Background(wx.Colour(255, 215, 0))
        fmt.ColumnHeader.CellPadding = 5
        fmt.ColumnHeader.GridPen = wx.Pen(wx.Colour(192, 192, 192), 1)

        fmt.Row.Font = wx.FFont(12, wx.FONTFAMILY_SWISS, face=rowFontName)
        fmt.Row.CellPadding = 5
        fmt.Row.GridPen = wx.Pen(wx.BLUE, 1, wx.DOT)
        fmt.Row.CanWrap = True

        fmt.Watermark.TextColor = wx.Colour(233, 150, 122)

        return fmt

#----------------------------------------------------------------------------

class BlockFormat(object):
    """
    A block format defines how a Block is formatted.

    These properties control the formatting of the matching Block:

    * CanWrap
        If the text for this block cannot fit horizontally, should be wrap to a new line (True)
        or should it be truncated (False)?
    * Font
        What font should be used to draw the text of this block
    * Padding
        How much padding should be applied to the block before the text or other decorations
        are drawn? This can be a numeric (which will be applied to all sides) or it can be
        a collection of the paddings to be applied to the various sides: (left, top, right, bottom).
    * TextAlignment
        How should text be aligned within this block? Can be wx.ALIGN_LEFT, wx.ALIGN_CENTER, or
        wx.ALIGN_RIGHT.
    * TextColor
        In what color should be text be drawn?

    The blocks that are based on cells (PageHeader, ColumnHeader, Row, PageFooter) can also
    have the following properties set:

    * AlwaysCenter
        Will the text in the cells be center aligned, regardless of other settings?
    * CellPadding
        How much padding should be applied to this cell before the text or other decorations
        are drawn? This can be a numeric (which will be applied to all sides) or it can be a
        collection of the paddings to be applied to the various sides: (left, top, right,
        bottom).
    * GridPen
        What Pen will be used to draw the grid lines of the cells?

    In addition to these properties, there are some methods which add various decorations to
    the blocks:

    * Background(color=wx.BLUE, toColor=None, space=0)

        This gives the block a solid color background (or a gradient background if *toColor*
        is not None). If *space* is not 0, *space* pixels will be subtracted from all sides
        from the space available to the block.

    * Frame(pen=None, space=0)

        Draw a rectangle around the block in the given pen

    * Line(side=wx.BOTTOM, color=wx.BLACK, width=1, toColor=None, space=0, pen=None)

        Draw a line on a given side of the block. If a pen is given, that is used to draw the
        line (and the other parameters are ignored), otherwise a solid line (or a gradient
        line is *toColor* is not None) of *width* pixels is drawn.

    """

    def __init__(self):
        """
        """
        self.padding = None
        self.decorations = list()
        self.font = wx.FFont(11, wx.FONTFAMILY_SWISS, face="Gill Sans")
        self.textColor = None
        self.textAlignment = wx.ALIGN_LEFT
        self.alwaysCenter = False
        self.canWrap = False

        #THINK: These attributes are only for grids. Should we have a GridBlockFormat object?
        self.cellPadding = None
        self.gridPen = None

    #----------------------------------------------------------------------------
    # Accessing

    def GetFont(self):
        """
        Return the font used by this format
        """
        return self.font

    def SetFont(self, font):
        """
        Set the font used by this format
        """
        self.font = font

    def GetTextAlignment(self):
        """
        Return the alignment of text in this format
        """
        return self.textAlignment

    def SetTextAlignment(self, alignment):
        """
        Set the alignment of text in this format
        """
        self.textAlignment = alignment

    def GetTextColor(self):
        """
        Return the color of text in this format
        """
        return self.textColor

    def SetTextColor(self, color):
        """
        Set the color of text in this format
        """
        self.textColor = color

    def GetPadding(self):
        """
        Get the padding around this format
        """
        return self.padding

    def SetPadding(self, padding):
        """
        Set the padding around this format

        Padding is either a single numeric (indicating the values on all sides)
        or a collection of paddings [left, top, right, bottom]
        """
        self.padding = self._MakePadding(padding)

    def GetCellPadding(self):
        """
        Get the padding around cells in this format
        """
        return self.cellPadding

    def SetCellPadding(self, padding):
        """
        Set the padding around cells in this format

        Padding is either a single numeric (indicating the values on all sides)
        or a collection of paddings [left, top, right, bottom]
        """
        self.cellPadding = self._MakePadding(padding)

    def GetGridPen(self):
        """
        Return the pen used to draw a grid in this format
        """
        return self.gridPen

    def SetGridPen(self, pen):
        """
        Set the pen used to draw a grid in this format
        """
        self.gridPen = pen
        if self.gridPen:
            # Other styles don't produce nice joins
            self.gridPen.SetCap(wx.CAP_BUTT)
            self.gridPen.SetJoin(wx.JOIN_MITER)

    def _MakePadding(self, padding):
        try:
            if len(padding) < 4:
                return (tuple(padding) + (0, 0, 0, 0))[:4]
            else:
                return padding
        except TypeError:
            return (padding,) * 4

    def GetAlwaysCenter(self):
        """
        Return if the text controlled by this format should always be centered?
        """
        return self.alwaysCenter

    def SetAlwaysCenter(self, value):
        """
        Remember if the text controlled by this format should always be centered?
        """
        self.alwaysCenter = value

    def GetCanWrap(self):
        """
        Return if the text controlled by this format can wrap to cover more than one line?
        """
        return self.canWrap

    def SetCanWrap(self, value):
        """
        Remember if the text controlled by this format can wrap to cover more than one line?
        """
        self.canWrap = value

    Font = property(GetFont, SetFont)
    Padding = property(GetPadding, SetPadding)
    TextAlignment = property(GetTextAlignment, SetTextAlignment)
    TextColor = property(GetTextColor, SetTextColor)
    CellPadding = property(GetCellPadding, SetCellPadding)
    GridPen = property(GetGridPen, SetGridPen)
    AlwaysCenter = property(GetAlwaysCenter, SetAlwaysCenter)
    CanWrap = property(GetCanWrap, SetCanWrap)

    # Misspellers of the world Untie!
    # Ok, ok... there're not really misspellings - just alternatives :)
    TextAlign = property(GetTextAlignment, SetTextAlignment)
    TextColour = property(GetTextColor, SetTextColor)

    #----------------------------------------------------------------------------
    # Calculations

    def CalculateCellPadding(self):
        """
        Return a four-tuple that indicates pixel padding (left, top, right, bottom)
        around cells in this format
        """
        if self.CellPadding:
            cellPadding = list(self.CellPadding)
        else:
            cellPadding = 0, 0, 0, 0

        if self.GridPen:
            penFactor = int((self.GridPen.GetWidth()+1)/2)
            cellPadding = [x + penFactor for x in cellPadding]

        return cellPadding

    #----------------------------------------------------------------------------
    # Decorations

    def Add(self, decoration):
        """
        Add the given decoration to those adorning blocks with this format
        """
        self.decorations.append(decoration)


    def Line(self, side=wx.BOTTOM, color=wx.BLACK, width=1, toColor=None, space=0, pen=None):
        """
        Add a line to our decorations.
        If a pen is given, we use a straight Line decoration, otherwise we use a
        coloured rectangle
        """
        if pen:
            self.Add(LineDecoration(side, pen, space))
        else:
            self.Add(RectangleDecoration(side, None, color, toColor, width, space))


    def Background(self, color=wx.BLUE, toColor=None, space=0):
        """
        Add a coloured background to the block
        """
        self.Add(RectangleDecoration(color=color, toColor=toColor, space=space))


    def Frame(self, pen=None, space=0):
        """
        Add a rectangle around this block
        """
        self.Add(RectangleDecoration(pen=pen, space=space))

    #----------------------------------------------------------------------------
    # Commands

    def SubtractPadding(self, bounds):
        """
        Subtract any padding used by this format from the given bounds
        """
        if self.padding is None:
            return bounds
        else:
            return RectUtils.InsetRect(bounds, self.padding)


    def SubtractDecorations(self, dc, bounds):
        """
        Subtract any space used by our decorations from the given bounds
        """
        for x in self.decorations:
            bounds = x.SubtractFrom(dc, bounds)
        return bounds


    def DrawDecorations(self, dc, bounds, block, over):
        """
        Draw our decorations on the given block
        """
        for x in self.decorations:
            if x.IsDrawOver() == over:
                x.DrawDecoration(dc, bounds, block)


#----------------------------------------------------------------------------

class Block(object):
    """
    A Block is a portion of a report that will stack vertically with other
    Block. A report consists of several Blocks.
    """

    def __init__(self, engine=None):
        self.engine = engine # This is also set when the block is added to a print engine

    #----------------------------------------------------------------------------
    # Accessing

    def GetFont(self):
        """
        Return Font that should be used to draw text in this block
        """
        return self.GetFormat().GetFont()


    def GetTextColor(self):
        """
        Return Colour that should be used to draw text in this block
        """
        return self.GetFormat().GetTextColor()


    def GetFormat(self):
        """
        Return the BlockFormat object that controls the formatting of this block
        """
        return self.engine.GetNamedFormat(self.__class__.__name__[:-5])


    def GetReducedBlockBounds(self, dc, bounds=None):
        """
        Return the bounds of this block once padding and decoration have taken their toll.
        """
        bounds = bounds or list(self.GetWorkBounds())
        fmt = self.GetFormat()
        bounds = fmt.SubtractPadding(bounds)
        bounds = fmt.SubtractDecorations(dc, bounds)
        return bounds


    def GetWorkBounds(self):
        """
        Return the boundaries of the work area for this block
        """
        return self.engine.workBounds


    def IsColumnHeadingsOnEachPage(self):
        """
        Should the column headers be report at the top of each new page?
        """
        return self.engine.reportFormat.IsColumnHeadingsOnEachPage


    def IncludeImages(self):
        """
        Should the images from the ListCtrl be printed in the report?
        """
        return self.engine.reportFormat.IncludeImages


    def IsShrinkToFit(self):
        """
        Should row blocks be shrunk to fit within the width of a page?
        """
        return self.engine.reportFormat.IsShrinkToFit


    def IsUseSubstitution(self):
        """
        Should the text values printed by this block have substitutions performed before being printed?

        This allows, for example, footers to have '%(currentPage)d of %(totalPages)d'
        """
        return True


    #----------------------------------------------------------------------------
    # Calculating

    def CalculateExtrasHeight(self, dc):
        """
        Return the height of the padding and decorations themselves
        """
        return 0 - RectUtils.Height(self.GetReducedBlockBounds(dc, [0, 0, 0, 0]))


    def CalculateExtrasWidth(self, dc):
        """
        Return the width of the padding and decorations themselves
        """
        return 0 - RectUtils.Width(self.GetReducedBlockBounds(dc, [0, 0, 0, 0]))


    def CalculateHeight(self, dc):
        """
        Return the heights of this block in pixels
        """
        return -1


    def CalculateTextHeight(self, dc, txt, bounds=None, font=None):
        """
        Return the height of the given txt in pixels
        """
        bounds = bounds or self.GetReducedBlockBounds(dc)
        font = font or self.GetFont()
        dc.SetFont(font)
        if self.GetFormat().CanWrap:
            return WordWrapRenderer.CalculateHeight(dc, txt, RectUtils.Width(bounds))
        else:
            # Calculate the height of one line. The 1000 pixel width
            # ensures that 'Wy' doesn't wrap, which might happen if bounds is narrow
            return WordWrapRenderer.CalculateHeight(dc, "Wy", 1000)


    def CanFit(self, height):
        """
        Can this block fit into the remaining work area on the page?
        """
        return height <= RectUtils.Height(self.GetWorkBounds())

    #----------------------------------------------------------------------------
    # Commands

    def Print(self, dc):
        """
        Print this Block.

        Return True if the Block has finished printing
        """
        if not self.ShouldPrint():
            return True

        bounds = self.CalculateBounds(dc)
        if not self.CanFit(RectUtils.Height(bounds)):
            return False

        if self.engine.shouldDrawBlocks:
            self.PreDraw(dc, bounds)
            self.Draw(dc, bounds)
            self.PostDraw(dc, bounds)

        self.ChangeWorkBoundsBy(RectUtils.Height(bounds))
        return True


    def ShouldPrint(self):
        """
        Should this block be printed?
        """
        # If this block does not have a format, it is simply skipped
        return self.GetFormat() is not None


    def CalculateBounds(self, dc):
        """
        Calculate the bounds of this block
        """
        height = self.CalculateHeight(dc)
        bounds = list(self.GetWorkBounds())
        bounds = RectUtils.SetHeight(bounds, height)
        return bounds


    def ChangeWorkBoundsBy(self, amt):
        """
        Move the top of our work bounds down by the given amount
        """
        RectUtils.MoveTopBy(self.engine.workBounds, amt)


    def Draw(self, dc, bounds):
        """
        Draw this block and its decorations allowing for any padding
        """
        fmt = self.GetFormat()
        decorationBounds = fmt.SubtractPadding(bounds)
        fmt.DrawDecorations(dc, decorationBounds, self, False)
        textBounds = fmt.SubtractDecorations(dc, list(decorationBounds))
        self.DrawSelf(dc, textBounds)
        fmt.DrawDecorations(dc, decorationBounds, self, True)


    def PreDraw(self, dc, bounds):
        """
        Executed before any drawing is done
        """
        pass


    def DrawSelf(self, dc, bounds):
        """
        Do the actual work of rendering this block.
        """
        pass


    def PostDraw(self, dc, bounds):
        """
        Executed after drawing has completed
        """
        pass


    def DrawText(self, dc, txt, bounds, font=None, alignment=wx.ALIGN_LEFT, valignment=wx.ALIGN_CENTRE,
                 image=None, color=None, canWrap=True, imageIndex=-1, listCtrl=None):
        """
        Draw the given text in the given DC according to the given characteristics.

        This is the workhorse text drawing method for our reporting engine.

        The *font*, *alignment*, and *color* attributes are applied to the drawn text.

        If *image* is not None, it will be drawn to the left of the text. All text is indented
        by the width of the image, even if the text is multi-line.

        If *imageIndex* is 0 or more and *listCtrl* is not None, the corresponding image from
        the ListCtrl's small image list will be drawn to the left of the text.

        If *canWrap* is True, the text will be wrapped to fit within the given bounds. If it is False,
        then the first line of *txt* will be truncated at the edge of the given *bounds*.
        """
        GAP_BETWEEN_IMAGE_AND_TEXT = 4

        def _CalcBitmapPosition(r, height):
            if valignment == wx.ALIGN_TOP:
                return RectUtils.Top(r)
            elif valignment == wx.ALIGN_CENTER:
                return RectUtils.CenterY(r) - height / 2
            elif valignment == wx.ALIGN_BOTTOM:
                return RectUtils.Bottom(r) - height
            else:
                return RectUtils.Top(r)

        # Draw any image
        if image:
            y = _CalcBitmapPosition(bounds, image.Height)
            dc.DrawBitmap(image, RectUtils.Left(bounds), y)
            RectUtils.MoveLeftBy(bounds, image.GetWidth()+GAP_BETWEEN_IMAGE_AND_TEXT)
        elif listCtrl and imageIndex >=0:
            imageList = listCtrl.GetImageList(wx.IMAGE_LIST_SMALL)
            y = _CalcBitmapPosition(bounds, imageList.GetSize(0)[1])
            imageList.Draw(imageIndex, dc, RectUtils.Left(bounds), y, wx.IMAGELIST_DRAW_TRANSPARENT)
            RectUtils.MoveLeftBy(bounds, imageList.GetSize(0)[0]+GAP_BETWEEN_IMAGE_AND_TEXT)

        # Draw the text
        dc.SetFont(font or self.GetFont())
        dc.SetTextForeground(color or self.GetTextColor() or wx.BLACK)
        if canWrap:
            WordWrapRenderer.DrawString(dc, txt, bounds, alignment, valignment)
        else:
            WordWrapRenderer.DrawTruncatedString(dc, txt, bounds, alignment, valignment)


    def PerformSubstitutions(self, strings):
        """
        Substituted % markers in the given collection of strings.
        """
        info = self.engine.GetSubstitutionInfo()
        try:
            # 'strings' could be a single string or a list of strings
            try:
                return strings % info
            except TypeError:
                return [x % info for x in strings]
        except ValueError:
            # We don't die if we get a substitution error - we just ignore it
            return strings

#----------------------------------------------------------------------------

class TextBlock(Block):
    """
    A TextBlock prints a string objects.
    """

    def ShouldPrint(self):
        """
        Should this block be printed?
        """
        # If the block has no text, it should not be printed
        if self.GetText():
            return Block.ShouldPrint(self)
        else:
            return False


    def GetText(self):
        return "Missing GetText() in class %s" % self.__class__.__name__


    def GetSubstitutedText(self):
        """
        Return the text for this block after all markers have been substituted
        """
        if self.IsUseSubstitution():
            return self.PerformSubstitutions(self.GetText())
        else:
            return self.GetText()


    def CalculateHeight(self, dc):
        """
        Return the heights of this block in pixels
        """
        textHeight = self.CalculateTextHeight(dc, self.GetSubstitutedText())
        extras = self.CalculateExtrasHeight(dc)
        return textHeight + extras


    def DrawSelf(self, dc, bounds):
        """
        Do the actual work of rendering this block.
        """
        fmt = self.GetFormat()
        self.DrawText(dc, self.GetSubstitutedText(), bounds, canWrap=fmt.CanWrap, alignment=fmt.TextAlignment)


#----------------------------------------------------------------------------

class CellBlock(Block):
    """
    A CellBlock is a Block whose data is presented in a cell format.
    """

    def __init__(self):
        self.scale = 1
        self.oldScale = 1

    #----------------------------------------------------------------------------
    # Accessing - Subclasses should override

    def GetCellWidths(self):
        """
        Return a list of the widths of the cells in this block.
        """
        return list()

    def GetTexts(self):
        """
        Return a list of the texts that should be drawn with the cells
        """
        return list()

    def GetAlignments(self):
        """
        Return a list indicating how the text within each cell is aligned.
        """
        return list()

    def GetImages(self):
        """
        Return a list of the images that should be drawn in each cell
        """
        return list()


    #----------------------------------------------------------------------------
    # Accessing


    def GetCombinedLists(self):
        """
        Return a collection of Buckets that hold all the values of the
        subclass-overridable collections above
        """
        buckets = [Bucket(cellWidth=x, text="", align=None, image=None) for x in self.GetCellWidths()]
        for (i, x) in enumerate(self.GetSubstitutedTexts()):
            buckets[i].text = x
        for (i, x) in enumerate(self.GetAlignments()):
            buckets[i].align = x

        if self.IncludeImages():
            for (i, x) in enumerate(self.GetImages()):
                buckets[i].image = x

        # Calculate where the cell contents should be drawn
        cellPadding = self.GetFormat().CalculateCellPadding()
        for x in buckets:
            x.innerCellWidth = max(0, x.cellWidth - (cellPadding[0] + cellPadding[2]))

        return buckets


    def GetListCtrl(self):
        """
        Return the ListCtrl that is behind this cell block.
        """
        return None


    def GetSubstitutedTexts(self):
        """
        Return a list of the texts that should be drawn with the cells
        """
        if self.IsUseSubstitution():
            return self.PerformSubstitutions(self.GetTexts())
        else:
            return self.GetTexts()


    #----------------------------------------------------------------------------
    # Calculating

    def CalculateHeight(self, dc):
        """
        Return the heights of this block in pixels
        """
        GAP_BETWEEN_IMAGE_AND_TEXT = 4

        # If cells can wrap, figure out the tallest, otherwise we just figure out the height of one line
        if self.GetFormat().CanWrap:
            font = self.GetFont()
            height = 0
            for x in self.GetCombinedLists():
                textWidth = x.innerCellWidth
                if self.GetListCtrl() and x.image != -1:
                    imageList = self.GetListCtrl().GetImageList(wx.IMAGE_LIST_SMALL)
                    textWidth -= imageList.GetSize(0)[0]+GAP_BETWEEN_IMAGE_AND_TEXT
                bounds = [0, 0, textWidth, 99999]
                height = max(height, self.CalculateTextHeight(dc, x.text, bounds, font))
        else:
            height = self.CalculateTextHeight(dc, "Wy")

        # We also have to allow for cell padding, on top of the normal padding and decorations
        cellPadding = self.GetFormat().CalculateCellPadding()
        return height + cellPadding[1] + cellPadding[3] + self.CalculateExtrasHeight(dc)


    def CalculateWidth(self, dc):
        """
        Calculate the total width of this block (cells plus padding)
        """
        return sum(x.cellWidth for x in self.GetCombinedLists()) + self.CalculateExtrasWidth(dc)

    #----------------------------------------------------------------------------
    # Commands

    def CalculateBounds(self, dc):
        """
        Calculate the bounds of this block
        """
        height = self.CalculateHeight(dc)
        bounds = list(self.GetWorkBounds())
        bounds = RectUtils.SetHeight(bounds, height)
        bounds = RectUtils.SetWidth(bounds, self.CalculateWidth(dc))
        bounds = RectUtils.MultiplyOrigin(bounds, 1 / self.scale)
        return bounds

    #def CanFit(self, height):
    #    height *= self.scale
    #    return Block.CanFit(self, height)

    def ChangeWorkBoundsBy(self, height):
        """
        Change our workbounds by our scaled height
        """
        Block.ChangeWorkBoundsBy(self, height * self.scale)


    def PreDraw(self, dc, bounds):
        """
        Apply our scale before performing any drawing
        """
        self.oldScale = dc.GetUserScale()
        dc.SetUserScale(self.scale * self.oldScale[0], self.scale * self.oldScale[1])


    def PostDraw(self, dc, bounds):
        """
        Restore the scaling to what it used to be
        """
        dc.SetUserScale(*self.oldScale)


    def DrawSelf(self, dc, bounds):
        """
        Do the actual work of rendering this block.
        """
        cellFmt = self.GetFormat()
        cellPadding = cellFmt.CalculateCellPadding()
        combined = self.GetCombinedLists()

        # Calculate cell boundaries
        cell = list(bounds)
        RectUtils.SetWidth(cell, 0)
        for x in combined:
            RectUtils.SetLeft(cell, RectUtils.Right(cell))
            RectUtils.SetWidth(cell, x.cellWidth)
            x.cell = list(cell)

        # Draw each cell
        font = self.GetFont()
        for x in combined:
            cellBounds = RectUtils.InsetRect(x.cell, cellPadding)
            self.DrawText(dc, x.text, cellBounds, font, x.align, imageIndex=x.image,
                          canWrap=cellFmt.CanWrap, listCtrl=self.GetListCtrl())

        if cellFmt.GridPen and combined:
            dc.SetPen(cellFmt.GridPen)
            dc.SetBrush(wx.TRANSPARENT_BRUSH)

            top = RectUtils.Top(bounds)
            bottom = RectUtils.Bottom(bounds)

            # Draw the interior dividers
            for x in combined[:-1]:
                right = RectUtils.Right(x.cell)
                dc.DrawLine(right, top, right, bottom)

            # Draw the surrounding frame
            left = RectUtils.Left(combined[0].cell)
            right = RectUtils.Right(combined[-1].cell)
            dc.DrawRectangle(left, top, right-left, bottom-top)


#----------------------------------------------------------------------------

class ThreeCellBlock(CellBlock):
    """
    A ThreeCellBlock divides its space evenly into three cells.
    """

    def GetCellWidths(self):
        """
        Return a list of the widths of the cells in this block
        """
        # We divide the available space between the non-empty cells
        numNonEmptyTexts = sum(1 for x in self.GetTexts() if x)
        if not numNonEmptyTexts:
            return (0, 0, 0)

        widths = list()
        width = round(RectUtils.Width(self.GetWorkBounds()) / numNonEmptyTexts)
        for x in self.GetTexts():
            if x:
                widths.append(width)
            else:
                widths.append(0)
        return widths


    def GetAlignments(self):
        """
        Return a list indicating how the text within each cell is aligned.
        """
        return (wx.ALIGN_LEFT, wx.ALIGN_CENTER_HORIZONTAL, wx.ALIGN_RIGHT)

#----------------------------------------------------------------------------

class ReportBlock(Block):
    """
    A ReportBlock is boot strap Block that represents an entire report.
    """

    #----------------------------------------------------------------------------
    # Commands

    def Print(self, dc):
        """
        Print this Block.

        Return True if the Block has finished printing
        """
        if not self.engine.listCtrls:
            return True

        # Print each ListView. Each list but the first starts on a separate page
        self.engine.AddBlock(ListBlock(*self.engine.listCtrls[0]))
        for (lv, title) in self.engine.listCtrls[1:]:
            self.engine.AddBlock(PageBreakBlock())
            self.engine.AddBlock(ListBlock(lv, title))

        return True


#----------------------------------------------------------------------------

class PageHeaderBlock(ThreeCellBlock):
    """
    A PageHeaderBlock appears at the top of every page.
    """

    def GetTexts(self):
        """
        Return the array of texts to be printed in the cells
        """
        return self.engine.pageHeader



#----------------------------------------------------------------------------

class PageFooterBlock(ThreeCellBlock):
    """
    A PageFooterBlock appears at the bottom of every page.
    """

    def GetTexts(self):
        """
        Return the array of texts to be printed in the cells
        """
        return self.engine.pageFooter


    #----------------------------------------------------------------------------
    # Printing


    def CalculateBounds(self, dc):
        """
        Calculate the bounds of this block
        """
        # Draw the footer at the bottom of the page
        height = self.CalculateHeight(dc)
        bounds = list(self.GetWorkBounds())
        return [RectUtils.Left(bounds), RectUtils.Bottom(bounds) - height,
                RectUtils.Width(bounds), height]


    def ChangeWorkBoundsBy(self, height):
        """
        The footer changes the bottom of the work bounds
        """
        RectUtils.MoveBottomBy(self.engine.workBounds, -height)


#----------------------------------------------------------------------------

class PageBreakBlock(Block):
    """
    A PageBreakBlock acts a page break.
    """

    #----------------------------------------------------------------------------
    # Commands

    def Print(self, dc):
        """
        Print this Block.

        Return True if the Block has finished printing
        """

        # Completely fill the remaining area on the page, forcing a page break
        bounds = self.GetWorkBounds()
        self.ChangeWorkBoundsBy(RectUtils.Height(bounds))

        return True

#----------------------------------------------------------------------------

class RunningBlockPusher(Block):
    """
    A RunningBlockPusher pushes (or pops) a running block onto the stack when it is executed.
    """

    def __init__(self, block, push=True):
        """
        """
        self.block = block
        self.push = push

    def Print(self, dc):
        """
        Print this Block.

        Return True if the Block has finished printing
        """
        if self.push:
            self.engine.AddRunningBlock(self.block)
        else:
            self.engine.RemoveRunningBlock(self.block)

        return True

#----------------------------------------------------------------------------

class ListBlock(Block):
    """
    A ListBlock handles the printing of an entire ListCtrl.
    """

    def __init__(self, lv, title):
        self.lv = lv
        self.title = title

    #----------------------------------------------------------------------------
    # Commands

    def Print(self, dc):
        """
        Print this Block.

        Return True if the Block has finished printing
        """

        cellWidths = self.CalculateCellWidths()
        boundsWidth = RectUtils.Width(self.GetWorkBounds())

        # Break the list into vertical slices. Each one but the first will be placed on a
        # new page.
        first = True
        for (left, right) in self.CalculateSlices(boundsWidth, cellWidths):
            if not first:
                self.engine.AddBlock(PageBreakBlock())
            self.engine.AddBlock(ListHeaderBlock(self.lv, self.title))
            self.engine.AddBlock(ListSliceBlock(self.lv, left, right, cellWidths))
            self.engine.AddBlock(ListFooterBlock(self.lv, ""))
            first = False

        return True


    def CalculateCellWidths(self):
        """
        Return a list of the widths of the cells in this lists
        """
        columnHeaderFmt = self.engine.GetNamedFormat("ColumnHeader")
        cellPadding = columnHeaderFmt.CalculateCellPadding()
        padding = cellPadding[0] + cellPadding[2]
        return [self.lv.GetColumnWidth(i) + padding for i in range(self.lv.GetColumnCount())]


    def CalculateSlices(self, maxWidth, columnWidths):
        """
        Return a list of integer pairs, where each pair represents
        the left and right columns that can fit into the width of one page
        """
        firstColumn = 0

        # If a GroupListView has a column just for the expand/collapse, don't include it
        if hasattr(self.lv, "useExpansionColumn") and self.lv.useExpansionColumn:
            firstColumn = 1

        # If we are shrinking to fit or all the columns fit, just return all columns
        if self.IsShrinkToFit() or (sum(columnWidths)) <= maxWidth:
            return [ [firstColumn, len(columnWidths)-1] ]

        pairs = list()
        left = firstColumn
        right = firstColumn
        while right < len(columnWidths):
            if (sum(columnWidths[left:right+1])) > maxWidth:
                if left == right:
                    pairs.append([left, right])
                    left += 1
                    right += 1
                else:
                    pairs.append([left, right-1])
                    left = right
            else:
                right += 1

        if left < len(columnWidths):
            pairs.append([left, right-1])

        return pairs


#----------------------------------------------------------------------------

class ListHeaderBlock(TextBlock):
    """
    A ListHeaderBlock is the title that comes before an ListCtrl.
    """

    def __init__(self, lv, title):
        self.lv = lv
        self.title = title

    def GetText(self):
        """
        Return the text that will be printed in this block
        """
        return self.title

#----------------------------------------------------------------------------

class ListFooterBlock(TextBlock):
    """
    A ListFooterBlock is the text that comes after an ListCtrl.
    """

    def __init__(self, lv, text):
        self.lv = lv
        self.text = text

    def GetText(self):
        """
        Return the text that will be printed in this block
        """
        return self.text


#----------------------------------------------------------------------------

class GroupTitleBlock(TextBlock):
    """
    A GroupTitleBlock is the title that comes before a list group.
    """

    def __init__(self, lv, group):
        self.lv = lv
        self.group = group

    def GetText(self):
        """
        Return the text that will be printed in this block
        """
        return self.group.title

#----------------------------------------------------------------------------

class ListSliceBlock(Block):
    """
    A ListSliceBlock prints a vertical slice of an ListCtrl.
    """

    def __init__(self, lv, left, right, allCellWidths):
        self.lv = lv
        self.left = left
        self.right = right
        self.allCellWidths = allCellWidths

    #----------------------------------------------------------------------------
    # Commands

    def Print(self, dc):
        """
        Print this Block.

        Return True if the Block has finished printing
        """
        # If we are shrinking our cells, calculate the shrink factor
        if self.IsShrinkToFit():
            scale = self.CalculateShrinkToFit(dc)
        else:
            scale = 1

        headerBlock = ColumnHeaderBlock(self.lv, self.left, self.right, scale, self.allCellWidths)
        self.engine.AddBlock(headerBlock)

        if self.IsColumnHeadingsOnEachPage():
            self.engine.AddBlock(RunningBlockPusher(headerBlock))

        # Are we printing a GroupListView?
        # We can't use isinstance() since ObjectListView may not be installed
        if hasattr(self.lv, "GetShowGroups") and self.lv.GetShowGroups():
            self.engine.AddBlock(GroupListRowsBlock(self.lv, self.left, self.right, scale, self.allCellWidths))
        else:
            self.engine.AddBlock(ListRowsBlock(self.lv, self.left, self.right, scale, self.allCellWidths))

        if self.IsColumnHeadingsOnEachPage():
            self.engine.AddBlock(RunningBlockPusher(headerBlock, False))

        return True

    def CalculateShrinkToFit(self, dc):
        """
        How much do we have to shrink our rows by to fit onto the page?
        """
        block = ColumnHeaderBlock(self.lv, self.left, self.right, 1, self.allCellWidths)
        block.engine = self.engine
        rowWidth = block.CalculateWidth(dc)
        boundsWidth = RectUtils.Width(self.GetWorkBounds())

        if rowWidth > boundsWidth:
            return float(boundsWidth) / float(rowWidth)
        else:
            return 1

#----------------------------------------------------------------------------

class ColumnBasedBlock(CellBlock):
    """
    A ColumnBasedBlock is a cell block that takes its width from the
    columns of a ListCtrl.

    This is an abstract class
    """

    def __init__(self, lv, left, right, scale, allCellWidths):
        self.lv = lv
        self.left = left
        self.right = right
        self.scale = scale
        self.allCellWidths = allCellWidths

    #----------------------------------------------------------------------------
    # Accessing - Subclasses should override

    def GetListCtrl(self):
        """
        Return the ListCtrl that is behind this cell block.
        """
        return self.lv


    def GetCellWidths(self):
        """
        Return the widths of the cells used in this block
        """
        #return [self.allCellWidths[i] for i in range(self.left, self.right+1)]
        return self.allCellWidths[self.left:self.right+1]

    #----------------------------------------------------------------------------
    # Utiltities

    def GetColumnAlignments(self, lv, left, right):
        """
        Return the alignments of the given slice of columns
        """
        listAlignments = [lv.GetColumn(i).GetAlign() for i in range(left, right+1)]
        mapping = {
            wx.LIST_FORMAT_LEFT: wx.ALIGN_LEFT,
            wx.LIST_FORMAT_RIGHT: wx.ALIGN_RIGHT,
            wx.LIST_FORMAT_CENTRE: wx.ALIGN_CENTRE,
        }
        return [mapping[x] for x in listAlignments]



#----------------------------------------------------------------------------

class ColumnHeaderBlock(ColumnBasedBlock):
    """
    A ColumnHeaderBlock prints a portion of the columns header in a ListCtrl.
    """

    #----------------------------------------------------------------------------
    # Accessing

    def GetTexts(self):
        """
        Return a list of the texts that should be drawn with the cells
        """
        return [self.lv.GetColumn(i).GetText() for i in range(self.left, self.right+1)]

    def GetAlignments(self):
        """
        Return a list indicating how the text within each cell is aligned.
        """
        if self.GetFormat().AlwaysCenter:
            return [wx.ALIGN_CENTRE for i in range(self.left, self.right+1)]
        else:
            return self.GetColumnAlignments(self.lv, self.left, self.right)

    def GetImages(self):
        """
        Return a list of the images that should be drawn in each cell
        """
        # For some reason, columns return 0 when they have no image, rather than -1 like they should
        images = list()
        for i in range(self.left, self.right+1):
            imageIndex = self.lv.GetColumn(i).GetImage()
            if imageIndex == 0:
                imageIndex = -1
            images.append(imageIndex)
        return images


    def IsUseSubstitution(self):
        """
        Should the text values printed by this block have substitutions performed before being printed?

        Normally, we don't want to substitute within values that comes from the ListCtrl.
        """
        return False


#----------------------------------------------------------------------------

class ListRowsBlock(Block):
    """
    A ListRowsBlock prints rows of an ListCtrl.
    """

    def __init__(self, lv, left, right, scale, allCellWidths):
        """
        """
        self.lv = lv
        self.left = left
        self.right = right
        self.scale = scale
        self.allCellWidths = allCellWidths
        self.currentIndex = 0
        self.totalRows = self.lv.GetItemCount()

    #----------------------------------------------------------------------------
    # Commands

    def Print(self, dc):
        """
        Print this Block.

        Return True if the Block has finished printing
        """
        # This block works by printing a single row and then rescheduling itself
        # to print the remaining rows after the current row has finished.

        if self.currentIndex < self.totalRows:
            self.engine.AddBlock(RowBlock(self.lv, self.currentIndex, self.left, self.right, self.scale, self.allCellWidths))
            self.currentIndex += 1
            self.engine.AddBlock(self)

        return True

#----------------------------------------------------------------------------

class GroupListRowsBlock(Block):
    """
    A GroupListRowsBlock prints rows of an GroupListView.
    """

    def __init__(self, lv, left, right, scale, allCellWidths):
        """
        """
        self.lv = lv # Must be a GroupListView
        self.left = left
        self.right = right
        self.scale = scale
        self.allCellWidths = allCellWidths

        self.currentIndex = 0
        self.totalRows = self.lv.GetItemCount()

    #----------------------------------------------------------------------------
    # Commands

    def Print(self, dc):
        """
        Print this Block.

        Return True if the Block has finished printing
        """
        # This block works by printing a single row and then rescheduling itself
        # to print the remaining rows after the current row has finished.

        if self.currentIndex >= self.totalRows:
            return True

        # If GetObjectAt() return an object, then it's a normal row.
        # Otherwise, if the innerList object isn't None, it must be a ListGroup
        # We can't use isinstance(x, GroupListView) because ObjectListView may not be installed
        if self.lv.GetObjectAt(self.currentIndex):
            self.engine.AddBlock(RowBlock(self.lv, self.currentIndex, self.left, self.right, self.scale, self.allCellWidths))
        elif self.lv.innerList[self.currentIndex]:
            self.engine.AddBlock(GroupTitleBlock(self.lv, self.lv.innerList[self.currentIndex]))

        # Schedule the printing of the remaining rows
        self.currentIndex += 1
        self.engine.AddBlock(self)

        return True


#----------------------------------------------------------------------------

class RowBlock(ColumnBasedBlock):
    """
    A RowBlock prints a vertical slice of a single row of an ListCtrl.
    """

    def __init__(self, lv, rowIndex, left, right, scale, allCellWidths):
        self.lv = lv
        self.rowIndex = rowIndex
        self.left = left
        self.right = right
        self.scale = scale
        self.allCellWidths = allCellWidths

    #----------------------------------------------------------------------------
    # Accessing


    def GetFont(self):
        """
        Return Font that should be used to draw text in this block
        """
        font = None
        if self.engine.reportFormat.UseListCtrlTextFormat and self.GetListCtrl():
            # Figure out what font is being used for this row in the list.
            # Unfortunately, there is no one way to find this information: virtual mode lists
            # have to be treated in a different manner from non-virtual lists.
            listCtrl = self.GetListCtrl()
            if listCtrl.IsVirtual():
                attr = listCtrl.OnGetItemAttr(self.rowIndex)
                if attr and attr.HasFont():
                    font = attr.GetFont()
            else:
                font = listCtrl.GetItemFont(self.rowIndex)

        if font and font.IsOk():
            return font
        else:
            return self.GetFormat().GetFont()


    def GetTextColor(self):
        """
        Return Colour that should be used to draw text in this block
        """
        color = None
        if self.engine.reportFormat.UseListCtrlTextFormat and self.GetListCtrl():
            # Figure out what text colour is being used for this row in the list.
            # Unfortunately, there is no one way to find this information: virtual mode lists
            # have to be treated in a different manner from non-virtual lists.
            listCtrl = self.GetListCtrl()
            if listCtrl.IsVirtual():
                attr = listCtrl.OnGetItemAttr(self.rowIndex)
                if attr and attr.HasTextColour():
                    color = attr.GetTextColour()
            else:
                color = listCtrl.GetItemTextColour(self.rowIndex)

        if color and color.IsOk():
            return color
        else:
            return self.GetFormat().GetTextColor()


    def IsUseSubstitution(self):
        """
        Should the text values printed by this block have substitutions performed before being printed?

        Normally, we don't want to substitute within values that comes from the ListCtrl.
        """
        return False

    #----------------------------------------------------------------------------
    # Overrides for CellBlock

    def GetTexts(self):
        """
        Return a list of the texts that should be drawn with the cells
        """
        return [self.lv.GetItem(self.rowIndex, i).GetText() for i in range(self.left, self.right+1)]

    def GetAlignments(self):
        """
        Return a list indicating how the text within each cell is aligned.
        """
        return self.GetColumnAlignments(self.lv, self.left, self.right)

    def GetImages(self):
        """
        Return a list of the images that should be drawn in each cell
        """
        return [self.lv.GetItem(self.rowIndex, i).GetImage() for i in range(self.left, self.right+1)]

    #def GetTexts(self):
    #    """
    #    Return a list of the texts that should be drawn with the cells
    #    """
    #    modelObjects = self.lv.GetObjectAt(self.rowIndex)
    #    return [self.lv.GetStringValueAt(modelObjects, i) for i in range(self.left, self.right+1)]
    #
    #def GetAlignments(self):
    #    """
    #    Return a list indicating how the text within each cell is aligned.
    #    """
    #    return [self.lv.columns[i].GetAlignment() for i in range(self.left, self.right+1)]
    #
    #def GetImages(self):
    #    """
    #    Return a list of the images that should be drawn in each cell
    #    """
    #    modelObjects = self.lv.GetObjectAt(self.rowIndex)
    #    return [self.lv.GetImageAt(modelObjects, i) for i in range(self.left, self.right+1)]


#----------------------------------------------------------------------------

class Decoration(object):
    """
    A Decoration add some visual effect to a Block (e.g. borders,
    background image, watermark). They can also reserve a chunk of their Blocks
    space for their own use.

    Decorations are added to a BlockFormat which is then applied to a ReportBlock.

    All the decorations for a block are drawn into the same area. If two decorations are
    added, they will draw over the top of each other. This is normally what is expected,
    but may sometimes be surprising. For example, if you add two Lines to the left of the
    same block, they will draw over the top of each other.

    """

    #----------------------------------------------------------------------------
    # Accessing

    def IsDrawOver(self):
        """
        Return True if this decoration should be drawn over it's block. If not,
        it will be drawn underneath
        """
        return False

    #----------------------------------------------------------------------------
    # Commands

    def SubtractFrom(self, dc, bounds):
        """
        Subtract the space used by this decoration from the given bounds
        """
        return bounds

    def DrawDecoration(self, dc, bounds, block):
        """
        Draw this decoration
        """
        pass

#----------------------------------------------------------------------------

class RectangleDecoration(Decoration):
    """
    A RectangleDecoration draw a rectangle around or on the side of a block.

    The rectangle can be hollow, solid filled or gradient-filled. It can have
    a frame drawn as well.

    """

    def __init__(self, side=None, pen=None, color=None, toColor=None, width=0, space=0):
        """
        If color is None, the rectangle will be hollow.
        If toColor is None, the rectangle will be filled with "color" otherwise it will be
        gradient-filled.
        If pen is not None, the rectangle will be framed with that pen.
        If no side is given, the rectangle will be drawn around the block. In that case,
        space can be a list giving the space on each side.
        """
        self.side = side
        self.pen = pen
        self.color = color
        self.toColor = toColor
        self.width = width
        self.space = space

    #----------------------------------------------------------------------------
    # Commands

    def SubtractFrom(self, dc, bounds):
        """
        Subtract the space used by this decoration from the given bounds
        """
        if self.side is None:
            return RectUtils.InsetBy(RectUtils.InsetBy(bounds, self.space), self.width)

        inset = self.space + self.width
        if self.side == wx.LEFT:    return RectUtils.MoveLeftBy(bounds, inset)
        if self.side == wx.RIGHT:   return RectUtils.MoveRightBy(bounds, -inset)
        if self.side == wx.TOP:     return RectUtils.MoveTopBy(bounds, inset)
        if self.side == wx.BOTTOM:  return RectUtils.MoveBottomBy(bounds, -inset)
        return bounds


    def DrawDecoration(self, dc, bounds, block):
        """
        Draw this decoration
        """
        rect = self._CalculateRect(bounds)

        if self.color:
            if self.toColor is None:
                dc.SetPen(wx.TRANSPARENT_PEN)
                dc.SetBrush(wx.Brush(self.color))
                dc.DrawRectangle(*rect)
            else:
                dc.GradientFillLinear(wx.Rect(*rect), self.color, self.toColor)

        if self.pen:
            dc.SetPen(self.pen)
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawRectangle(*rect)


    def _CalculateRect(self, bounds):
        """
        Calculate the rectangle that this decoration is going to paint
        """
        if self.side is None:
            return bounds
        if self.side == wx.LEFT:
            return (RectUtils.Left(bounds), RectUtils.Top(bounds), self.width, RectUtils.Height(bounds))
        if self.side == wx.RIGHT:
            return (RectUtils.Right(bounds) - self.width, RectUtils.Top(bounds), self.width, RectUtils.Height(bounds))
        if self.side == wx.TOP:
            return (RectUtils.Left(bounds), RectUtils.Top(bounds), RectUtils.Width(bounds), self.width)
        if self.side == wx.BOTTOM:
            return (RectUtils.Left(bounds), RectUtils.Bottom(bounds) - self.width, RectUtils.Width(bounds), self.width)

        return bounds

#----------------------------------------------------------------------------

class LineDecoration(Decoration):
    """
    A LineDecoration draws a line on the side of a decoration.
    """

    def __init__(self, side=wx.BOTTOM, pen=None, space=0):
        self.side = side
        self.pen = pen
        self.space = space

    #----------------------------------------------------------------------------
    # Commands

    def SubtractFrom(self, dc, bounds):
        """
        Subtract the space used by this decoration from the given bounds
        """
        inset = self.space
        if self.pen is not None:
            inset += self.pen.GetWidth()

        if self.side == wx.LEFT:    return RectUtils.MoveLeftBy(bounds, inset)
        if self.side == wx.RIGHT:   return RectUtils.MoveRightBy(bounds, -inset)
        if self.side == wx.TOP:     return RectUtils.MoveTopBy(bounds, inset)
        if self.side == wx.BOTTOM:  return RectUtils.MoveBottomBy(bounds, -inset)
        return bounds


    def DrawDecoration(self, dc, bounds, block):
        """
        Draw this decoration
        """
        if self.pen == None:
            return

        if self.side == wx.LEFT:
            pt1 = RectUtils.TopLeft(bounds)
            pt2 = RectUtils.BottomLeft(bounds)
        elif self.side == wx.RIGHT:
            pt1 = RectUtils.TopRight(bounds)
            pt2 = RectUtils.BottomRight(bounds)
        elif self.side == wx.TOP:
            pt1 = RectUtils.TopLeft(bounds)
            pt2 = RectUtils.TopRight(bounds)
        elif self.side == wx.BOTTOM:
            pt1 = RectUtils.BottomLeft(bounds)
            pt2 = RectUtils.BottomRight(bounds)

        dc.SetPen(self.pen)
        dc.DrawLine(pt1[0], pt1[1], pt2[0], pt2[1])

#----------------------------------------------------------------------------

class WatermarkDecoration(Decoration):
    """
    A WatermarkDecoration draws an angled line of text over each page.

    The watermark is rotated around the center of the page.

    If *over* is True, the watermark will be printed on top of the page.
    Otherwise, it will be printed under the page.

    """

    def __init__(self, text, font=None, color=None, angle=30, over=True):
        """
        """
        self.text = text
        self.color = color or wx.Color(128, 128, 128, 128)
        self.font = font or wx.FFont(128, wx.SWISS, 0)
        self.angle = angle
        self.over = over

    def IsDrawOver(self):
        """
        Should this decoration be drawn over the rest of page?
        """
        return self.over

    def DrawDecoration(self, dc, bounds, block):
        """
        Draw the decoration
        """
        dc.SetFont(self.font)
        dc.SetTextForeground(self.color)

        # Rotate the text around the center of the page
        cx, cy = RectUtils.Center(bounds)
        w, h = dc.GetTextExtent(self.text)

        x = cx - w/2
        y = cy - h/2 + (w/2 * math.sin(math.radians(self.angle)))

        dc.DrawRotatedText(self.text, x, y, self.angle)

#----------------------------------------------------------------------------

class ImageDecoration(Decoration):
    """
    A ImageDecoration draws an image over (or under) the given block.

    NB: Printer contexts do not honor alpha channels.
    """

    def __init__(self, image=None, horizontalAlign=wx.CENTER, verticalAlign=wx.CENTER, over=True):
        """
        image must be either an wx.Image or a wx.Bitmap
        """
        self.horizontalAlign = horizontalAlign
        self.verticalAlign = verticalAlign
        self.over = True

        self.bitmap = image
        if isinstance(image, wx.Image):
            self.bitmap = wx.BitmapFromImage(image)

    def DrawDecoration(self, dc, bounds, block):
        """
        Draw the decoration
        """
        if not self.bitmap:
            return

        if self.horizontalAlign == wx.LEFT:
            x = RectUtils.Left(bounds)
        elif self.horizontalAlign == wx.RIGHT:
            x = RectUtils.Right(bounds) - self.bitmap.Width
        else:
            x = RectUtils.CenterX(bounds) - self.bitmap.Width/2

        if self.verticalAlign == wx.TOP:
            y = RectUtils.Top(bounds)
        elif self.verticalAlign == wx.BOTTOM:
            y = RectUtils.Bottom(bounds) - self.bitmap.Height
        else:
            y = RectUtils.CenterY(bounds) - self.bitmap.Height/2

        dc.DrawBitmap(self.bitmap, x, y, True)


#----------------------------------------------------------------------------

class Bucket(object):
    """
    General purpose, hold-all data object
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        strs = ["%s=%r" % kv for kv in self.__dict__.items()]
        return "Bucket(" + ", ".join(strs) + ")"

#----------------------------------------------------------------------------

class RectUtils:
    """
    Static rectangle utilities.

    Rectangles are a list or tuple of 4-elements: [left, top, width, height]
    """

    #----------------------------------------------------------------------------
    # Accessing

    @staticmethod
    def Left(r): return r[0]

    @staticmethod
    def Top(r): return r[1]

    @staticmethod
    def Width(r): return r[2]

    @staticmethod
    def Height(r): return r[3]

    @staticmethod
    def Right(r): return r[0] + r[2]

    @staticmethod
    def Bottom(r): return r[1] + r[3]

    @staticmethod
    def TopLeft(r): return [r[0], r[1]]

    @staticmethod
    def TopRight(r): return [r[0] + r[2], r[1]]

    @staticmethod
    def BottomLeft(r): return [r[0], r[1] + r[3]]

    @staticmethod
    def BottomRight(r): return [r[0] + r[2], r[1] + r[3]]

    @staticmethod
    def CenterX(r): return r[0] + r[2]/2

    @staticmethod
    def CenterY(r): return r[1] + r[3]/2

    @staticmethod
    def Center(r): return [r[0] + r[2]/2, r[1] + r[3]/2]

    #----------------------------------------------------------------------------
    # Modifying

    @staticmethod
    def SetLeft(r, l):
        r[0] = l
        return r

    @staticmethod
    def SetTop(r, t):
        r[1] = t
        return r

    @staticmethod
    def SetWidth(r, w):
        r[2] = w
        return r

    @staticmethod
    def SetHeight(r, h):
        r[3] = h
        return r

    @staticmethod
    def MoveLeftBy(r, delta):
        r[0] += delta
        r[2] -= delta
        return r

    @staticmethod
    def MoveTopBy(r, delta):
        r[1] += delta
        r[3] -= delta
        return r

    @staticmethod
    def MoveRightBy(r, delta):
        r[2] += delta
        return r

    @staticmethod
    def MoveBottomBy(r, delta):
        r[3] += delta
        return r

    #----------------------------------------------------------------------------
    # Calculations

    @staticmethod
    def InsetBy(r, delta):
        if delta is None:
            return r
        try:
            delta[0] # is it indexable?
            return RectUtils.InsetRect(r, delta)
        except:
            return RectUtils.InsetRect(r, (delta, delta, delta, delta))

    @staticmethod
    def InsetRect(r, r2):
        if r2 is None:
            return r
        else:
            return [r[0] + r2[0], r[1] + r2[1], r[2] - (r2[0] + r2[2]), r[3] - (r2[1] + r2[3])]

    @staticmethod
    def MultiplyOrigin(r, factor):
        return [r[0]*factor, r[1]*factor, r[2], r[3]]

#----------------------------------------------------------------------------
# TESTING ONLY
#----------------------------------------------------------------------------

if __name__ == '__main__':
    import wx
    from ObjectListView import ObjectListView, FastObjectListView, GroupListView, ColumnDefn

    # Where can we find the Example module?
    import sys
    sys.path.append("../Examples")

    import ExampleModel
    import ExampleImages

    class MyFrame(wx.Frame):
        def __init__(self, *args, **kwds):
            kwds["style"] = wx.DEFAULT_FRAME_STYLE
            wx.Frame.__init__(self, *args, **kwds)

            self.panel = wx.Panel(self, -1)
            #self.lv = ObjectListView(self.panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
            self.lv = GroupListView(self.panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
            #self.lv = FastObjectListView(self.panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)

            sizer_2 = wx.BoxSizer(wx.VERTICAL)
            sizer_2.Add(self.lv, 1, wx.ALL|wx.EXPAND, 4)
            self.panel.SetSizer(sizer_2)
            self.panel.Layout()

            sizer_1 = wx.BoxSizer(wx.VERTICAL)
            sizer_1.Add(self.panel, 1, wx.EXPAND)
            self.SetSizer(sizer_1)
            self.Layout()

            musicImage = self.lv.AddImages(ExampleImages.getMusic16Bitmap(), ExampleImages.getMusic32Bitmap())
            artistImage = self.lv.AddImages(ExampleImages.getUser16Bitmap(), ExampleImages.getUser32Bitmap())

            self.lv.SetColumns([
                ColumnDefn("Title", "left", 200, "title", imageGetter=musicImage),
                ColumnDefn("Artist", "left", 150, "artist", imageGetter=artistImage),
                ColumnDefn("Last Played", "left", 100, "lastPlayed"),
                ColumnDefn("Size", "center", 100, "sizeInBytes"),
                ColumnDefn("Rating", "center", 100, "rating"),
             ])

            #self.lv.CreateCheckStateColumn()
            self.lv.SetSortColumn(self.lv.columns[2])
            self.lv.SetObjects(ExampleModel.GetTracks())

            wx.CallLater(50, self.run)

        def run(self):
            printer = ListCtrlPrinter(self.lv, "Playing with ListCtrl Printing")
            printer.ReportFormat = ReportFormat.Normal()
            printer.ReportFormat.WatermarkFormat(over=True)
            printer.ReportFormat.IsColumnHeadingsOnEachPage = True

            #printer.ReportFormat.Page.Add(ImageDecoration(ExampleImages.getGroup32Bitmap(), wx.RIGHT, wx.BOTTOM))

            #printer.PageHeader("%(listTitle)s") # nice idea but not possible at the moment
            printer.PageHeader = "Playing with ListCtrl Printing"
            printer.PageFooter = ("Bright Ideas Software", "%(date)s", "%(currentPage)d of %(totalPages)d")
            printer.Watermark = "Sloth!"

            #printer.PageSetup()
            printer.PrintPreview(self)


    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
