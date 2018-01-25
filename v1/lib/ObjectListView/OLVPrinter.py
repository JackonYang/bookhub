# -*- coding: utf-8 -*-
#!/usr/bin/env python
#----------------------------------------------------------------------------
# Name:         OLVPrinter.py
# Author:       Phillip Piper
# Created:      17 July 2008
# SVN-ID:       $Id$
# Copyright:    (c) 2008 by Phillip Piper, 2008
# License:      wxWindows license
#----------------------------------------------------------------------------
# Change log:
# 2008/07/17  JPP   Initial version
#----------------------------------------------------------------------------
# To do:

"""
An OLVPrinter takes an ObjectListView and turns it into a pretty report.

As always, the goal is for this to be as easy to use as possible. A typical
usage should be as simple as::

   printer = OLVPrinter(self.myOlv, "My Report Title")
   printer.PrintPreview()

"""

import wx

from ObjectListView import GroupListView
from WordWrapRenderer import WordWrapRenderer

#======================================================================

class OLVPrinter(wx.Printout):
    """
    An OLVPrinter creates a pretty report from an ObjectListView.
    """

    def __init__(self, objectListView=None, title="ObjectListView Printing"):
        """
        """
        wx.Printout.__init__(self, title)
        self.engine = ReportEngine()

        self.printData = wx.PrintData()
        self.printData.SetPaperId(wx.PAPER_A4)
        self.printData.SetPrintMode(wx.PRINT_MODE_PRINTER)

        if objectListView is not None:
            self.engine.AddListCtrl(objectListView, title)

    #----------------------------------------------------------------------------
    # Accessing

    def HasPage(self, page):
        print "HasPage(%d)" % page
        return page <= self.engine.GetTotalPages()

    def GetPageInfo(self):
        print "GetPageInfo"
        return (1, self.engine.GetTotalPages(), 1, 1)

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

    ReportFormat = property(GetReportFormat, SetReportFormat)

    #----------------------------------------------------------------------------
    # Commands

    def PageSetup(self):
        """
        Show a Page Setup dialog that will change the configuration of this printout
        """
        psdd = wx.PageSetupDialogData(self.printData)
        psdd.CalculatePaperSizeFromId()
        dlg = wx.PageSetupDialog(self, psdd)
        dlg.ShowModal()

        # this makes a copy of the wx.PrintData instead of just saving
        # a reference to the one inside the PrintDialogData that will
        # be destroyed when the dialog is destroyed
        self.printData = wx.PrintData(dlg.GetPageSetupData().GetPrintData())

        dlg.Destroy()


    def PrintPreview(self, parent=None, title="ObjectListView Print Preview", bounds=(20, 50, 800, 800)):
        """
        Show a Print Preview of this report
        """
        data = wx.PrintDialogData(self.printData)
        #TODO: Implement some proper way to copy the printer
        #forPrinter = OLVPrinter()
        #forPrinter.ReportFormat = self.ReportFormat
        #forPrinter.engine.objectListViews = list(self.engine.objectListViews)
        self.preview = wx.PrintPreview(self, None, data)

        if not self.preview.Ok():
            return False

        pfrm = wx.PreviewFrame(self.preview, parent, title)

        pfrm.Initialize()
        pfrm.SetPosition(bounds[0:2])
        pfrm.SetSize(bounds[2:4])
        pfrm.Show(True)

        return True


    def DoPrint(self, parent=None):
        """
        Send the report to the configured printer
        """
        pdd = wx.PrintDialogData(self.printData)
        printer = wx.Printer(pdd)

        if printer.Print(parent, self, True):
            self.printData = wx.PrintData(printer.GetPrintDialogData().GetPrintData())
        else:
            wx.MessageBox("There was a problem printing.\nPerhaps your current printer is not set correctly?", "Printing", wx.OK)

        printout.Destroy()


    #----------------------------------------------------------------------------
    # Event handlers

    def OnPreparePrinting(self):
        """
        Prepare for printing. This event is sent before any of the others
        """
        print "OnPreparePrinting"
        print "self.GetDC() = %s" % self.GetDC()
        self.engine.CalculateTotalPages(self.GetDC())
        self.engine.StartPrinting()

    def OnBeginDocument(self, start, end):
        """
        Begin printing one copy of the document. Return False to cancel the job
        """
        print "OnBeginDocument(%d, %d)" % (start, end)
        if not super(OLVPrinter, self).OnBeginDocument(start, end):
            return False

        return True

    def OnEndDocument(self):
        print "OnEndDocument"
        super(OLVPrinter, self).OnEndDocument()

    def OnBeginPrinting(self):
        print "OnBeginPrinting"
        super(OLVPrinter, self).OnBeginPrinting()

    def OnEndPrinting(self):
        print "OnEndPrinting"
        super(OLVPrinter, self).OnEndPrinting()

    def OnPrintPage(self, page):
        print "OnPrintPage(%d)" % page
        return self.engine.PrintPage(self.GetDC(), page)


#======================================================================

class ReportEngine(object):
    """
    A ReportEngine handles all the work of actually producing a report.
    """

    def __init__(self):
        """
        """
        self.currentPage = -1
        self.totalPages = -1
        self.blocks = list()
        self.blockInsertionIndex = 0
        self.objectListViews = list()

        self.reportFormat = ReportFormat()

        self.isColumnHeadingsOnEachPage = True
        self.alwaysCenterColumnHeader = True
        self.reportHeaderText = "Report Header Text"
        self.reportFooterText = "Report Footer Text"
        self.pageHeaderText = "This is the header"
        self.pageFooterText = "This is the footer"
        self.isPrintSelectionOnly = False
        self.isShrinkToFit = False
        self.canCellsWrap = True

        self.watermarkText = "WATERMARK"
        self.watermarkFont = None
        self.watermarkColor = None

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

    #----------------------------------------------------------------------------
    # Calculating

    def CalculateTotalPages(self, dc):
        """
        Do the work of calculating how many pages this report will occupy?

        This is expensive because it basically prints the whole report.
        """
        self.StartPrinting()
        self.totalPages = 1
        while self.PrintOnePage(dc, self.totalPages):
            self.totalPages += 1
        dc.Clear()


    def CalculateBounds(self, dc):
        """
        Calculate our page and work bounds
        """
        self.pageBounds = (0, 0) + dc.GetSizeTuple()
        self.workBounds = list(self.pageBounds)

    #----------------------------------------------------------------------------
    # Commands

    def AddBlock(self, block):
        """
        Add the given block at the current insertion point
        """
        self.blocks.insert(self.blockInsertionIndex, block)
        self.blockInsertionIndex += 1
        block.engine = self


    def AddListCtrl(self, objectListView, title=None):
        """
        Add the given list to those that will be printed by this report.
        """
        if objectListView.InReportView():
            self.objectListViews.append([objectListView, title])


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
        self.AddRunningBlock(PageHeaderBlock(self))
        self.AddRunningBlock(PageFooterBlock(self))

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


    def PrintPage(self, dc, pageNumber):
        """
        Print the given page on the given device context.
        """
        #try:
        #    pdc = wx.GCDC(dc)
        #except:
        #    pdc = dc
        pdc = dc

        # If the request page isn't next in order, we have to restart
        # the printing process and advance until we reach the desired page
        if pageNumber != self.currentPage + 1:
            print "Skipping pages..."
            self.StartPrinting()
            for i in range(1, pageNumber):
                self.PrintOnePage(pdc, i)
            dc.Clear()
            print "...finished skipping."

        return self.PrintOnePage(pdc, pageNumber)


    def PrintOnePage(self, dc, pageNumber):
        """
        Print the current page on the given device context.

        Return true if there is still more to print.
        """
        self.currentPage = pageNumber
        self.CalculateBounds(dc)
        self.ApplyPageDecorations(dc)

        for x in self.runningBlocks:
            x.Print(dc)

        while len(self.blocks) and self.blocks[0].Print(dc):
            self.DropCurrentBlock()

        return len(self.blocks) > 0


    def ApplyPageDecorations(self, dc):
        """
        """
        fmt = self.GetNamedFormat("Page")

        # Draw the page decorations
        bounds = list(self.pageBounds)
        fmt.DrawDecorations(dc, bounds, self)

        # Subtract the area used from the work area
        self.workBounds = fmt.SubtractDecorations(dc, self.workBounds)


#======================================================================

class ReportFormat(object):
    """
    A ReportFormat defines completely how a report is formatted.

    It holds a collection of BlockFormat objects which control the
    formatting of individual blocks of the report

    """

    def __init__(self):
        """
        """
        self.formats = [
            "Page",
            "ReportHeader",
            "PageHeader",
            "ListHeader",
            "GroupTitle",
            "List",
            "ColumnHeader",
            "ListRows",
            "Row",
            "ListFooter",
            "PageFooter",
            "ReportFooter"
        ]
        for x in self.formats:
            setattr(self, x, BlockFormat())

    def GetNamedFormat(self, name):
        """
        Return the format used in to format a block with the given name.
        """
        return getattr(self, name)

    @staticmethod
    def Normal(fontName="Arial"):
        """
        Return a reasonable default format for a report
        """
        fmt = ReportFormat()
        fmt.PageHeader.Font = wx.FFont(24, wx.FONTFAMILY_DEFAULT, face=fontName)
        fmt.PageHeader.TextAlignment = wx.ALIGN_CENTRE
        fmt.PageHeader.Add(FrameDecoration(pen=wx.Pen(wx.BLUE, 1), space=5))
        #fmt.PageHeader.Add(LineDecoration(pen=wx.Pen(wx.BLUE, 2), space=5))

        fmt.ReportHeader.Font = wx.FFont(36, wx.FONTFAMILY_DEFAULT, face=fontName)
        fmt.ReportHeader.TextColor = wx.RED
        fmt.ReportHeader.Padding = (0, 12, 0, 12)

        fmt.ListHeader.Add(LineDecoration(side=Decoration.BOTTOM, pen=wx.Pen(wx.GREEN, 1)))

        fmt.PageFooter.Font = wx.FFont(12, wx.FONTFAMILY_DEFAULT, face=fontName)
        fmt.PageFooter.TextAlignment = wx.ALIGN_RIGHT
        fmt.PageFooter.Add(LineDecoration(side=Decoration.TOP, pen=wx.Pen(wx.BLUE, 1), space=3))

        fmt.Row.Font = wx.FFont(12, wx.FONTFAMILY_DEFAULT, face=fontName)
        #fmt.ColumnHeader.CellPadding=25
        fmt.ColumnHeader.GridPen=wx.Pen(wx.RED, 1)
        fmt.Row.CellPadding=(10, 10, 0, 10)
        fmt.Row.GridPen=wx.Pen(wx.BLUE, 1)
        #fmt.ColumnHeader.Add(FrameDecoration(pen=wx.Pen(wx.RED, 1)))
        #fmt.Row.Add(FrameDecoration(pen=wx.Pen(wx.RED, 10)))
        #fmt.Row.Add(LineDecoration(side=Decoration.BOTTOM, pen=wx.Pen(wx.GREEN, 1)))

        return fmt

#======================================================================

class BlockFormat(object):
    """
    A block format defines how a Block is formatted.

    """

    def __init__(self):
        """
        """
        self.padding = None
        self.decorations = list()
        self.font = wx.FFont(14, wx.FONTFAMILY_SWISS, face="Gill Sans")
        self.textColor = None
        self.textAlignment = wx.ALIGN_LEFT
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

    Font = property(GetFont, SetFont)
    Padding = property(GetPadding, SetPadding)
    TextAlignment = property(GetTextAlignment, SetTextAlignment)
    TextColor = property(GetTextColor, SetTextColor)
    TextColour = property(GetTextColor, SetTextColor)
    CellPadding = property(GetCellPadding, SetCellPadding)
    GridPen = property(GetGridPen, SetGridPen)

    #----------------------------------------------------------------------------
    # Decorations

    def Add(self, decoration):
        """
        Add the given decoration to those adorning blocks with this format
        """
        self.decorations.append(decoration)

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


    def SubtractCellPadding(self, bounds):
        """
        Subtract any cell padding used by this format from the given bounds
        """
        if self.cellPadding is None:
            return bounds
        else:
            return RectUtils.InsetRect(bounds, self.cellPadding)


    def SubtractDecorations(self, dc, bounds):
        """
        Subtract any space used by our decorations from the given bounds
        """
        for x in self.decorations:
            bounds = x.SubtractFrom(dc, bounds)
        return bounds


    def DrawDecorations(self, dc, bounds, block):
        """
        Draw our decorations on the given block
        """
        for x in self.decorations:
            x.DrawDecoration(dc, bounds, block)


#======================================================================

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
        if fmt:
            bounds = fmt.SubtractPadding(bounds)
            bounds = fmt.SubtractDecorations(dc, bounds)
        return bounds


    def GetWorkBounds(self):
        """
        Return the boundaries of the work area for this block
        """
        return self.engine.workBounds


    def ChangeWorkBoundsTopBy(self, amt):
        """
        Move the top of our work bounds down by the given amount
        """
        RectUtils.MoveTopBy(self.engine.workBounds, amt)

    #----------------------------------------------------------------------------
    # Calculating

    def CalculateExtrasHeight(self, dc):
        """
        Return the height of the padding and decorations themselves
        """
        return 0 - RectUtils.Height(self.GetReducedBlockBounds(dc, [0, 0, 0, 0]))


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
        return WordWrapRenderer.CalculateHeight(dc, txt, RectUtils.Width(bounds))


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
        # If this block does not have a format, it is simply skipped
        if not self.GetFormat():
            return True

        height = self.CalculateHeight(dc)
        if not self.CanFit(height):
            return False

        bounds = self.GetWorkBounds()
        bounds = RectUtils.SetHeight(list(bounds), height)
        self.Draw(dc, bounds)
        self.ChangeWorkBoundsTopBy(height)
        return True


    def Draw(self, dc, bounds):
        """
        Draw this block and its decorations allowing for any padding
        """
        fmt = self.GetFormat()
        bounds = fmt.SubtractPadding(bounds)
        fmt.DrawDecorations(dc, bounds, self)
        bounds = fmt.SubtractDecorations(dc, bounds)
        self.DrawSelf(dc, bounds)


    def DrawSelf(self, dc, bounds):
        """
        Do the actual work of rendering this block.
        """
        pass


    def DrawText(self, dc, txt, bounds, font=None, alignment=wx.ALIGN_LEFT, image=None, color=None):
        """
        """
        dc.SetFont(font or self.GetFont())
        dc.SetTextForeground(color or self.GetTextColor() or wx.BLACK)
        WordWrapRenderer.DrawString(dc, txt, bounds, alignment, allowClipping=False)



#======================================================================

class TextBlock(Block):
    """
    A TextBlock prints a string objects.
    """

    def GetText(self):
        return "Missing GetText() in class %s" % self.__class__.__name__

    def CalculateHeight(self, dc):
        """
        Return the heights of this block in pixels
        """
        textHeight = self.CalculateTextHeight(dc, self.GetText())
        extras = self.CalculateExtrasHeight(dc)
        return textHeight + extras

    def DrawSelf(self, dc, bounds):
        """
        Do the actual work of rendering this block.
        """
        self.DrawText(dc, self.GetText(), bounds, alignment=self.GetFormat().TextAlignment)


#======================================================================

class CellBlock(Block):
    """
    A CellBlock is a Block whose data is presented in a cell format.
    """

    #----------------------------------------------------------------------------
    # Accessing - Subclasses should override

    def GetCellWidths(self):
        """
        Return a list of the widths of the cells in this block
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

    def CanCellsWrap(self):
        """
        Return True if the text values can wrap within a cell, producing muliline cells
        """
        return self.engine.canCellsWrap

    def GetCombinedLists(self):
        """
        Return a collection of Buckets that hold all the values of the
        subclass-overridable collections above
        """
        buckets = [Bucket(cellWidth=x, text="", align=None, image=None) for x in self.GetCellWidths()]
        for (i, x) in enumerate(self.GetTexts()):
            buckets[i].text = x
        for (i, x) in enumerate(self.GetImages()):
            buckets[i].image = x
        for (i, x) in enumerate(self.GetAlignments()):
            buckets[i].align = x

        return buckets

    #----------------------------------------------------------------------------
    # Utiltities

    def GetColumnAlignments(self, olv, left, right):
        """
        Return the alignments of the given slice of columns
        """
        listAlignments = [olv.GetColumn(i).GetAlign() for i in range(left, right+1)]
        mapping = {
            wx.LIST_FORMAT_LEFT: wx.ALIGN_LEFT,
            wx.LIST_FORMAT_RIGHT: wx.ALIGN_RIGHT,
            wx.LIST_FORMAT_CENTRE: wx.ALIGN_CENTRE,
        }
        return [mapping[x] for x in listAlignments]


    def GetColumnWidths(self, olv, left, right):
        """
        Return a list of the widths of the given slice of columns
        """
        return [olv.GetColumnWidth(i) for i in range(left, right+1)]

    #----------------------------------------------------------------------------
    # Calculating

    def CalculateHeight(self, dc):
        """
        Return the heights of this block in pixels
        """
        # If cells can wrap, figure out the tallest, otherwise we just figure out the height of one line
        if self.CanCellsWrap():
            font = self.GetFont()
            height = 0
            for x in self.GetCombinedLists():
                bounds = [0, 0, x.cellWidth, 99999]
                height = max(height, self.CalculateTextHeight(dc, x.text, bounds, font))
        else:
            height = self.CalculateTextHeight(dc, "Wy")

        cellPadding = self._CalculateCellPadding(self.GetFormat())
        return height + cellPadding[1] + cellPadding[3] + self.CalculateExtrasHeight(dc)

    def _CalculateCellPadding(self, cellFmt):
        if cellFmt.CellPadding:
            cellPadding = list(cellFmt.CellPadding)
        else:
            cellPadding = 0, 0, 0, 0

        if cellFmt.GridPen:
            penFactor = int((cellFmt.GridPen.GetWidth()+1)/2)
            cellPadding = [x + penFactor for x in cellPadding]

        return cellPadding

    #----------------------------------------------------------------------------
    # Commands

    def DrawSelf(self, dc, bounds):
        """
        Do the actual work of rendering this block.
        """
        cellFmt = self.GetFormat()
        cellPadding = self._CalculateCellPadding(cellFmt)
        combined = self.GetCombinedLists()

        # Calculate cell boundaries
        cell = list(bounds)
        cell[2] = 0
        for x in combined:
            RectUtils.SetLeft(cell, RectUtils.Right(cell))
            RectUtils.SetWidth(cell, x.cellWidth + cellPadding[0] + cellPadding[2])
            x.cell = list(cell)
            #dc.SetPen(wx.BLACK_PEN)
            #dc.DrawRectangle(*cell)

        # Draw each cell
        font = self.GetFont()
        for x in combined:
            cellBounds = RectUtils.InsetRect(x.cell, cellPadding)
            self.DrawText(dc, x.text, cellBounds, font, x.align, x.image)
            #dc.SetPen(wx.RED_PEN)
            #dc.DrawRectangle(*cellBounds)

        if cellFmt.GridPen and combined:
            dc.SetPen(cellFmt.GridPen)
            dc.SetBrush(wx.TRANSPARENT_BRUSH)

            top = RectUtils.Top(combined[0].cell)
            bottom = RectUtils.Bottom(combined[0].cell)

            # Draw the interior dividers
            for x in combined[:-1]:
                right = RectUtils.Right(x.cell)
                dc.DrawLine(right, top, right, bottom)

            # Draw the surrounding frame
            left = RectUtils.Left(combined[0].cell)
            right = RectUtils.Right(combined[-1].cell)
            dc.DrawRectangle(left, top, right-left, bottom-top)


#======================================================================

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
        self.engine.AddBlock(ReportHeaderBlock())

        # Print each ListView. Each list but the first starts on a separate page
        first = True
        for (olv, title) in self.engine.objectListViews:
            if not first:
                self.engine.AddBlock(PageBreakBlock())
            self.engine.AddBlock(ListBlock(olv, title))
            first = False

        self.engine.AddBlock(ReportFooterBlock())
        return True

#======================================================================

class ReportHeaderBlock(TextBlock):
    """
    A ReportHeader is a text message that appears at the very beginning
    of a report.
    """

    def GetText(self):
        return self.engine.reportHeaderText

#======================================================================

class ReportFooterBlock(TextBlock):
    """
    A ReportFooter is a text message that appears at the very end of a report.
    """

    def GetText(self):
        return self.engine.reportFooterText


#======================================================================

class PageHeaderBlock(TextBlock):
    """
    A PageHeaderBlock appears at the top of every page.
    """

    def GetText(self):
        return self.engine.pageHeaderText



#======================================================================

class PageFooterBlock(TextBlock):
    """
    A PageFooterBlock appears at the bottom of every page.
    """

    def GetText(self):
        return self.engine.pageFooterText


    #----------------------------------------------------------------------------
    # Printing


    def Print(self, dc):
        """
        Print this block.
        """
        height = self.CalculateHeight(dc)

        # Draw the footer at the bottom of the page
        bounds = self.GetWorkBounds()
        bounds = [RectUtils.Left(bounds), RectUtils.Bottom(bounds) - height,
                  RectUtils.Width(bounds), height]
        self.Draw(dc, bounds)

        # The footer changes the bottom of the work area
        RectUtils.MoveBottomBy(self.engine.workBounds, height)
        return True


#======================================================================

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
        self.ChangeWorkBoundsTopBy(RectUtils.Height(bounds))

        return True

#======================================================================

class ListBlock(Block):
    """
    A ListBlock handles the printing of an entire ObjectListView.
    """

    def __init__(self, olv, title):
        self.olv = olv
        self.title = title

    #----------------------------------------------------------------------------
    # Commands

    def Print(self, dc):
        """
        Print this Block.

        Return True if the Block has finished printing
        """

        # Break the list into vertical slices. Each one but the first
        # will be placed on a new page.
        first = True
        for (left, right) in self.CalculateListSlices():
            if not first:
                self.engine.AddBlock(PageBreakBlock())
            self.engine.AddBlock(ListHeaderBlock(self.olv, self.title))
            self.engine.AddBlock(ListSliceBlock(self.olv, left, right))
            self.engine.AddBlock(ListFooterBlock(self.olv, ""))
            first = False

        return True

    def CalculateListSlices(self):
        """
        Return a list of integer pairs, where each pair represents
        the left and right columns that can fit into the width of one page
        """
        boundsWidth = RectUtils.Width(self.GetWorkBounds())
        columnWidths = [self.olv.GetColumnWidth(i) for i in range(self.olv.GetColumnCount())]
        return self.CalculateSlices(boundsWidth, columnWidths)

    def CalculateSlices(self, maxWidth, columnWidths):
        """
        Return a list of integer pairs, where each pair represents
        the left and right columns that can fit into the width of one page
        """
        firstColumn = 0

        # If a GroupListView has a column just for the expand/collapse, don't include it
        if hasattr(self.olv, "useExpansionColumn") and self.olv.useExpansionColumn:
            firstColumn = 1

        # If we are shrinking to fit or all the columns fit, just return all columns
        if self.engine.isShrinkToFit or (sum(columnWidths)) <= maxWidth:
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


#======================================================================

class ListHeaderBlock(TextBlock):
    """
    A ListHeaderBlock is the title that comes before an ObjectListView.
    """

    def __init__(self, olv, title):
        self.olv = olv
        self.title = title

    def GetText(self):
        return self.title

#======================================================================

class ListFooterBlock(TextBlock):
    """
    A ListFooterBlock is the text that comes before an ObjectListView.
    """

    def __init__(self, olv, text):
        self.olv = olv
        self.text = text

    def GetText(self):
        return self.text


#======================================================================

class GroupTitleBlock(TextBlock):
    """
    A GroupTitleBlock is the title that comes before a list group.
    """

    def __init__(self, olv, group):
        self.olv = olv
        self.group = group

    def GetText(self):
        return self.group.title

#======================================================================

class ListSliceBlock(Block):
    """
    A ListSliceBlock prints a vertical slice of an ObjectListView.
    """

    def __init__(self, olv, left, right):
        self.olv = olv
        self.left = left
        self.right = right


    #----------------------------------------------------------------------------
    # Commands

    def Print(self, dc):
        """
        Print this Block.

        Return True if the Block has finished printing
        """
        self.engine.AddBlock(ColumnHeaderBlock(self.olv, self.left, self.right))
        if hasattr(self.olv, "GetShowGroups") and self.olv.GetShowGroups():
            self.engine.AddBlock(GroupListRowsBlock(self.olv, self.left, self.right))
        else:
            self.engine.AddBlock(ListRowsBlock(self.olv, self.left, self.right))
        return True


#======================================================================

class ColumnHeaderBlock(CellBlock):
    """
    A ColumnHeaderBlock prints a portion of the columns header in
    an ObjectListView.
    """

    def __init__(self, olv, left, right):
        self.olv = olv
        self.left = left
        self.right = right

    #----------------------------------------------------------------------------
    # Accessing - Subclasses should override

    def GetCellWidths(self):
        """
        Return a list of the widths of the cells in this block
        """
        return self.GetColumnWidths(self.olv, self.left, self.right)

    def GetTexts(self):
        """
        Return a list of the texts that should be drawn with the cells
        """
        return [self.olv.GetColumn(i).GetText() for i in range(self.left, self.right+1)]

    def GetAlignments(self):
        """
        Return a list indicating how the text within each cell is aligned.
        """
        if self.engine.alwaysCenterColumnHeader:
            return [wx.ALIGN_CENTRE for i in range(self.left, self.right+1)]
        else:
            return self.GetColumnAlignments(olv, self.left, self.right)

    def GetImages(self):
        """
        Return a list of the images that should be drawn in each cell
        """
        return [self.olv.GetColumn(i).GetImage() for i in range(self.left, self.right+1)]


#======================================================================

class ListRowsBlock(Block):
    """
    A ListRowsBlock prints rows of an ObjectListView.
    """

    def __init__(self, olv, left, right):
        """
        """
        self.olv = olv
        self.left = left
        self.right = right
        self.currentIndex = 0
        self.totalRows = self.olv.GetItemCount()

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
            self.engine.AddBlock(RowBlock(self.olv, self.currentIndex, self.left, self.right))
            self.currentIndex += 1
            self.engine.AddBlock(self)

        return True

#======================================================================

class GroupListRowsBlock(Block):
    """
    A GroupListRowsBlock prints rows of an GroupListView.
    """

    def __init__(self, olv, left, right):
        """
        """
        self.olv = olv # Must be a GroupListView
        self.left = left
        self.right = right

        self.currentIndex = 0
        self.totalRows = self.olv.GetItemCount()

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
        if self.olv.GetObjectAt(self.currentIndex):
            self.engine.AddBlock(RowBlock(self.olv, self.currentIndex, self.left, self.right))
        elif self.olv.innerList[self.currentIndex]:
            self.engine.AddBlock(GroupTitleBlock(self.olv, self.olv.innerList[self.currentIndex]))

        # Schedule the printing of the remaining rows
        self.currentIndex += 1
        self.engine.AddBlock(self)

        return True


#======================================================================

class RowBlock(CellBlock):
    """
    A RowBlock prints a vertical slice of a single row of an ObjectListView.
    """

    def __init__(self, olv, rowIndex, left, right):
        self.olv = olv
        self.rowIndex = rowIndex
        self.left = left
        self.right = right


    def GetCellWidths(self):
        """
        Return a list of the widths of the cells in this block
        """
        return self.GetColumnWidths(self.olv, self.left, self.right)

    def GetTexts(self):
        """
        Return a list of the texts that should be drawn with the cells
        """
        return [self.olv.GetItem(self.rowIndex, i).GetText() for i in range(self.left, self.right+1)]

    def GetAlignments(self):
        """
        Return a list indicating how the text within each cell is aligned.
        """
        return self.GetColumnAlignments(self.olv, self.left, self.right)

    def GetImages(self):
        """
        Return a list of the images that should be drawn in each cell
        """
        return [self.olv.GetItem(self.rowIndex, i).GetImage() for i in range(self.left, self.right+1)]

#======================================================================

class Decoration(object):
    """
    A Decoration add some visual effect to a Block (e.g. borders,
    background image, watermark). They can also reserve a chunk of their Blocks
    space for their own use.

    Decorations are added to a BlockFormat which is then applied to a ReportBlock
    """

    LEFT = 0
    RIGHT = 1
    TOP = 2
    BOTTOM = 3

    def __init__(self, *args):
        pass

    #----------------------------------------------------------------------------
    # Commands

    def SubtractFrom(self, dc, bounds):
        """
        Subtract the space used by this decoration from the given bounds
        """
        return bounds

    def SubtractInternalFrom(self, dc, bounds):
        """
        Subtract the space used by this decoration when used within a block.
        This is currently only used for cells within a grid.
        """
        return bounds

    def DrawDecoration(self, dc, bounds, block):
        """
        Draw this decoration
        """
        pass

#----------------------------------------------------------------------------

class BackgroundDecoration(Decoration):
    """
    A BackgroundDecoration paints the background of a block
    """

    def __init__(self, color=None):
        self.color = color

    def DrawDecoration(self, dc, bounds, block):
        """
        Draw this decoration
        """
        if self.color is None:
            return
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(self.color))
        dc.DrawRectangle(*bounds)

#----------------------------------------------------------------------------

class FrameDecoration(Decoration):
    """
    A FrameDecoration a frame around a block
    """

    def __init__(self, pen=None, space=0, corner=None):
        self.pen = pen
        self.space = space
        self.corner = corner

    def SubtractFrom(self, dc, bounds):
        """
        Subtract the space used by this decoration from the given bounds
        """
        inset = self.space
        if self.pen is not None:
            inset += self.pen.GetWidth()

        return RectUtils.InsetBy(bounds, inset)

    def DrawDecoration(self, dc, bounds, block):
        """
        Draw this decoration
        """
        if self.pen is None:
            return
        # We want to draw our decoration within the given bounds. Fat pens are drawn half
        # either side of the coords, so we contract our coords so that fat pens don't
        # cause drawing outside our bounds.
        if self.pen.GetWidth() > 1:
            rect = RectUtils.InsetBy(bounds, self.pen.GetWidth()/2)
        else:
            rect = bounds
        dc.SetPen(self.pen)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        if self.corner:
            dc.DrawRoundedRectangle(rect[0], rect[1], rect[2], rect[3], self.corner)
        else:
            dc.DrawRectangle(*rect)

#----------------------------------------------------------------------------

class LineDecoration(Decoration):
    """
    A LineDecoration draws a line on the side of a decoration.
    """

    def __init__(self, side=Decoration.BOTTOM, pen=None, space=0):
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

        if self.side == Decoration.LEFT:
            return RectUtils.MoveLeftBy(bounds, inset)
        if self.side == Decoration.RIGHT:
            return RectUtils.MoveRightBy(bounds, inset)
        if self.side == Decoration.TOP:
            return RectUtils.MoveTopBy(bounds, inset)
        if self.side == Decoration.BOTTOM:
            return RectUtils.MoveBottomBy(bounds, inset)
        return bounds


    def DrawDecoration(self, dc, bounds, block):
        """
        Draw this decoration
        """
        if self.pen == None:
            return

        if self.side == Decoration.LEFT:
            pt1 = RectUtils.TopLeft(bounds)
            pt2 = RectUtils.BottomLeft(bounds)
        elif self.side == Decoration.RIGHT:
            pt1 = RectUtils.TopRight(bounds)
            pt2 = RectUtils.BottomRight(bounds)
        elif self.side == Decoration.TOP:
            pt1 = RectUtils.TopLeft(bounds)
            pt2 = RectUtils.TopRight(bounds)
        elif self.side == Decoration.BOTTOM:
            pt1 = RectUtils.BottomLeft(bounds)
            pt2 = RectUtils.BottomRight(bounds)
        else:
            return

        dc.SetPen(self.pen)
        dc.DrawLine(pt1[0], pt1[1], pt2[0], pt2[1])


#======================================================================

class Bucket(object):
    """
    General purpose, hold-all data object
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        strs = ["%s=%r" % kv for kv in self.__dict__.items()]
        return "Bucket(" + ", ".join(strs) + ")"

#======================================================================

class RectUtils:
    """
    Static rectangle utilities
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
        r[2] -= delta
        return r

    @staticmethod
    def MoveBottomBy(r, delta):
        r[3] -= delta
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

#======================================================================
# TESTING ONLY
#======================================================================

if __name__ == '__main__':
    import wx
    from ObjectListView import ObjectListView, GroupListView, ColumnDefn

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
            self.olv = ObjectListView(self.panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
            self.olv = GroupListView(self.panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
            #self.olv = FastObjectListView(self.panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
            #self.olv = VirtualObjectListView(self.panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)

            sizer_2 = wx.BoxSizer(wx.VERTICAL)
            sizer_2.Add(self.olv, 1, wx.ALL|wx.EXPAND, 4)
            self.panel.SetSizer(sizer_2)
            self.panel.Layout()

            sizer_1 = wx.BoxSizer(wx.VERTICAL)
            sizer_1.Add(self.panel, 1, wx.EXPAND)
            self.SetSizer(sizer_1)
            self.Layout()

            groupImage = self.olv.AddImages(ExampleImages.getGroup16Bitmap(), ExampleImages.getGroup32Bitmap())
            userImage = self.olv.AddImages(ExampleImages.getUser16Bitmap(), ExampleImages.getUser32Bitmap())
            musicImage = self.olv.AddImages(ExampleImages.getMusic16Bitmap(), ExampleImages.getMusic32Bitmap())

            self.olv.SetColumns([
                ColumnDefn("Title", "left", 120, "title", imageGetter=musicImage),
                ColumnDefn("Artist", "left", 120, "artist", imageGetter=groupImage),
                ColumnDefn("Last Played", "left", 100, "lastPlayed"),
                ColumnDefn("Size", "center", 100, "sizeInBytes"),
                ColumnDefn("Rating", "center", 100, "rating")
            ])
            #self.olv.CreateCheckStateColumn()
            self.olv.SetSortColumn(self.olv.columns[2])
            self.olv.SetObjects(ExampleModel.GetTracks())

            wx.CallLater(50, self.run)

        def run(self):
            printer = OLVPrinter(self.olv, "First ObjectListView Report")
            printer.ReportFormat = ReportFormat.Normal()

            #fmt.PageHeader.Font = wx.FFont(36, wx.FONTFAMILY_SWISS, face="Gill Sans")
            #fmt.PageHeader.Add(BackgroundDecoration(wx.BLUE))
            #fmt.PageHeader.Add(LineDecoration(side=Decoration.TOP, pen=wx.Pen(wx.RED, 5), space=0))
            #fmt.PageHeader.Add(LineDecoration(pen=wx.BLACK_PEN, space=0))
            #
            #fmt.PageFooter.Font = wx.FFont(12, wx.FONTFAMILY_SWISS, face="Gill Sans")
            #fmt.PageFooter.Add(BackgroundDecoration(wx.GREEN))
            #fmt.PageFooter.Add(LineDecoration(pen=wx.Pen(wx.BLUE, 5), space=0))
            #fmt.PageFooter.Add(LineDecoration(side=Decoration.TOP, pen=wx.RED_PEN, space=0))

            printer.PrintPreview(self)


    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
