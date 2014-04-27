# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Name:         CellEditor.py
# Author:       Phillip Piper
# Created:      3 April 2008
# SVN-ID:       $Id$
# Copyright:    (c) 2008 by Phillip Piper, 2008
# License:      wxWindows license
#----------------------------------------------------------------------------
# Change log:
# 2009/06/09  JPP   All cell editors start life 0 sized to prevent flickering
# 2008/05/26  JPP   Fixed pyLint annoyances
# 2008/04/04  JPP   Initial version complete
#----------------------------------------------------------------------------
# To do:
# - there has to be a better DateTimeEditor somewhere!!

"""
The *CellEditor* module provides some editors for standard types that can be installed
in an *ObjectListView*. It also provides a *Registry* that maps between standard types
and functions that will create editors for that type.

Cell Editors

    A cell editor can be any subclass of wx.Window provided that it supports the
    following protocol:

    SetValue(self, value)
        The editor should show the given value for editing

    GetValue(self)
        The editor should return the value that it holds. Return None to indicate
        an invalid value. The returned value should be of the correct type, i.e.
        don't return a string if the editor was registered for the bool type.

    The editor should invoke FinishCellEdit() on its parent ObjectListView when it
    loses focus or when the user commits the change by pressing Return or Enter.

    The editor should invoke CancelCellEdit() on its parent ObjectListView when
    the user presses Escape.

Editor Registry

    The editor registry remembers a function that will be called to create
    an editor for a given type.
"""

__author__ = "Phillip Piper"
__date__ = "3 May 2008"
__version__ = "1.0"

import datetime
import wx

#======================================================================
# Editor Registry

# Module level variable
_cellEditorRegistrySingleton = None

def CellEditorRegistry():
    """
    Return the registry that is managing type to creator functions
    """
    global _cellEditorRegistrySingleton

    if _cellEditorRegistrySingleton is None:
        _cellEditorRegistrySingleton = EditorRegistry()

    return _cellEditorRegistrySingleton


class EditorRegistry:
    """
    An *EditorRegistry* manages a mapping of types onto creator functions.

    When called, creator functions will create the appropriate kind of cell editor
    """

    def __init__(self):
        self.typeToFunctionMap = {}

        # Standard types and their creator functions
        self.typeToFunctionMap[str] = self._MakeStringEditor
        self.typeToFunctionMap[unicode] = self._MakeStringEditor
        self.typeToFunctionMap[bool] = self._MakeBoolEditor
        self.typeToFunctionMap[int] = self._MakeIntegerEditor
        self.typeToFunctionMap[long] = self._MakeLongEditor
        self.typeToFunctionMap[float] = self._MakeFloatEditor
        self.typeToFunctionMap[datetime.datetime] = self._MakeDateTimeEditor
        self.typeToFunctionMap[datetime.date] = self._MakeDateEditor
        self.typeToFunctionMap[datetime.time] = self._MakeTimeEditor

        # TODO: Install editors for mxDateTime if installed

    def GetCreatorFunction(self, aValue):
        """
        Return the creator function that is register for the type of the given value.
        Return None if there is no registered function for the type.
        """
        return self.typeToFunctionMap.get(type(aValue), None)

    def RegisterCreatorFunction(self, aType, aFunction):
        """
        Register the given function to be called when we need an editor for the given type.

        The function must accept three parameter: an ObjectListView, row index, and subitem index.
        It should return a wxWindow that is parented on the listview, and that responds to:

           - SetValue(newValue)

           - GetValue() to return the value shown in the editor

        """
        self.typeToFunctionMap[aType] = aFunction

    #----------------------------------------------------------------------------
    # Creator functions for standard types

    @staticmethod
    def _MakeStringEditor(olv, rowIndex, subItemIndex):
        return BaseCellTextEditor(olv, subItemIndex)

    @staticmethod
    def _MakeBoolEditor(olv, rowIndex, subItemIndex):
        return BooleanEditor(olv)

    @staticmethod
    def _MakeIntegerEditor(olv, rowIndex, subItemIndex):
        return IntEditor(olv, subItemIndex, validator=NumericValidator())

    @staticmethod
    def _MakeLongEditor(olv, rowIndex, subItemIndex):
        return LongEditor(olv, subItemIndex)

    @staticmethod
    def _MakeFloatEditor(olv, rowIndex, subItemIndex):
        return FloatEditor(olv, subItemIndex, validator=NumericValidator("0123456789-+eE."))

    @staticmethod
    def _MakeDateTimeEditor(olv, rowIndex, subItemIndex):
        dte = DateTimeEditor(olv, subItemIndex)

        column = olv.columns[subItemIndex]
        if isinstance(column.stringConverter, basestring):
            dte.formatString = column.stringConverter

        return dte

    @staticmethod
    def _MakeDateEditor(olv, rowIndex, subItemIndex):
        dte =  DateEditor(olv, style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY | wx.WANTS_CHARS)
        #dte.SetValidator(MyValidator(olv))
        return dte

    @staticmethod
    def _MakeTimeEditor(olv, rowIndex, subItemIndex):
        editor = TimeEditor(olv, subItemIndex)

        column = olv.columns[subItemIndex]
        if isinstance(column.stringConverter, basestring):
            editor.formatString = column.stringConverter

        return editor

#======================================================================
# Cell editors


class BooleanEditor(wx.Choice):
    """This is a simple editor to edit a boolean value that can be used in an
    ObjectListView"""

    def __init__(self, *args, **kwargs):
        kwargs["choices"] = ["True", "False"]
        wx.Choice.__init__(self, *args, **kwargs)

    def GetValue(self):
        "Get the value from the editor"
        return self.GetSelection() == 0

    def SetValue(self, value):
        "Put a new value into the editor"
        if value:
            self.Select(0)
        else:
            self.Select(1)

#----------------------------------------------------------------------------

class BaseCellTextEditor(wx.TextCtrl):
    """This is a base text editor for text-like editors used in an ObjectListView"""

    def __init__(self, olv, subItemIndex, **kwargs):
        style = wx.TE_PROCESS_ENTER | wx.TE_PROCESS_TAB
        # Allow for odd case where parent isn't an ObjectListView
        if hasattr(olv, "columns"):
            if olv.HasFlag(wx.LC_ICON):
                style |= (wx.TE_CENTRE | wx.TE_MULTILINE)
            else:
                style |= olv.columns[subItemIndex].GetAlignmentForText()
        wx.TextCtrl.__init__(self, olv, style=style, size=(0,0), **kwargs)

        # With the MULTILINE flag, the text control always has a vertical
        # scrollbar, which looks stupid. I don't know how to get rid of it.
        # This doesn't do it:
        # self.ToggleWindowStyle(wx.VSCROLL)

#----------------------------------------------------------------------------

class IntEditor(BaseCellTextEditor):
    """This is a text editor for integers for use in an ObjectListView"""

    def GetValue(self):
        "Get the value from the editor"
        s = wx.TextCtrl.GetValue(self).strip()
        try:
            return int(s)
        except ValueError:
            return None

    def SetValue(self, value):
        "Put a new value into the editor"
        if isinstance(value, int):
            value = repr(value)
        wx.TextCtrl.SetValue(self, value)

#----------------------------------------------------------------------------

class LongEditor(BaseCellTextEditor):
    """This is a text editor for long values for use in an ObjectListView"""

    def GetValue(self):
        "Get the value from the editor"
        s = wx.TextCtrl.GetValue(self).strip()
        try:
            return long(s)
        except ValueError:
            return None

    def SetValue(self, value):
        "Put a new value into the editor"
        if isinstance(value, long):
            value = repr(value)
        wx.TextCtrl.SetValue(self, value)

#----------------------------------------------------------------------------

class FloatEditor(BaseCellTextEditor):
    """This is a text editor for floats for use in an ObjectListView.

    Because of the trouble of precisely converting floats to strings,
    this editor sometimes behaves a little strangely."""

    def GetValue(self):
        "Get the value from the editor"
        s = wx.TextCtrl.GetValue(self).strip()
        try:
            return float(s)
        except ValueError:
            return None

    def SetValue(self, value):
        "Put a new value into the editor"
        if isinstance(value, float):
            value = repr(value)
        wx.TextCtrl.SetValue(self, value)

#----------------------------------------------------------------------------

class DateTimeEditor(BaseCellTextEditor):
    """
    A DateTimeEditor allows the user to enter a date/time combination, where the time is optional
    and many formats of date and time are allowed.

    The control accepts these date formats (in all cases, the year can be only 2 digits):
      - '31/12/2008'
      - '2008/12/31'
      - '12/31/2008'
      - '31 December 2008'
      - '31 Dec 2008'
      - 'Dec 31 2008'
      - 'December 31 2008'

    Slash character can also be '-' or ' '. Consecutive whitespace are collapsed.

    The control accepts these time formats:
      - '23:59:59'
      - '11:59:59pm'
      - '23:59'
      - '11:59pm'
      - '11pm'

    The colons are required. The am/pm is case insensitive.

    The implementation uses a brute force approach to parsing the data.
    """
    # Acceptable formats:
    # '31/12/2008', '2008/12/31', '12/31/2008', '31 December 2008', '31 Dec 2008', 'Dec 31 2007'
    # second line is the same but with two-digit year.
    # slash character can also be '-' or ' '. Consecutive whitespace are collapsed.
    STD_DATE_FORMATS = ['%d %m %Y', '%Y %m %d', '%m %d %Y', '%d %B %Y', '%d %b %Y', '%b %d %Y', '%B %d %Y',
                        '%d %m %y', '%y %m %d', '%m %d %y', '%d %B %y', '%d %b %y', '%b %d %y', '%B %d %y']

    STD_DATE_WITHOUT_YEAR_FORMATS = ['%d %m', '%m %d', '%d %B', '%d %b', '%B %d', '%b %d']

    # Acceptable formats: '23:59:59', '11:59:59pm', '23:59', '11:59pm', '11pm'
    STD_TIME_FORMATS = ['%H:%M:%S', '%I:%M:%S %p', '%H:%M', '%I:%M %p', '%I %p']

    # These separators are treated as whitespace
    STD_SEPARATORS = "/-,"

    def __init__(self, *args, **kwargs):
        BaseCellTextEditor.__init__(self, *args, **kwargs)
        self.formatString = "%X %x"

        self.allDateTimeFormats = []
        for dtFmt in self.STD_DATE_FORMATS:
            self.allDateTimeFormats.append(dtFmt)
            for timeFmt in self.STD_TIME_FORMATS:
                self.allDateTimeFormats.append("%s %s" % (dtFmt, timeFmt))

        self.allDateTimeWithoutYearFormats = []
        for dtFmt in self.STD_DATE_WITHOUT_YEAR_FORMATS:
            self.allDateTimeWithoutYearFormats.append(dtFmt)
            for timeFmt in self.STD_TIME_FORMATS:
                self.allDateTimeWithoutYearFormats.append("%s %s" % (dtFmt, timeFmt))


    def SetValue(self, value):
        "Put a new value into the editor"
        if isinstance(value, datetime.datetime):
            value = value.strftime(self.formatString)
        wx.TextCtrl.SetValue(self, value)


    def GetValue(self):
        "Get the value from the editor"
        s = wx.TextCtrl.GetValue(self).strip()
        return self._ParseDateTime(s)


    def _ParseDateTime(self, s):
        # Try the installed format string first
        try:
            return datetime.datetime.strptime(s, self.formatString)
        except ValueError:
            pass

        for x in self.STD_SEPARATORS:
            s = s.replace(x, " ")

        # Because of the logic of strptime, we have to check shorter patterns first.
        # For example:
        #   "31 12" matches "%d %m %y" => datetime(2012, 1, 3, 0, 0) ??
        # but we want:
        #   "31 12" to match "%d %m" => datetime(1900, 12, 31, 0, 0)
        # JPP 4/4/2008 Python 2.5.1
        for fmt in self.allDateTimeWithoutYearFormats:
            try:
                dt = datetime.datetime.strptime(s, fmt)
                return dt.replace(year=datetime.datetime.today().year)
            except ValueError:
                pass

        for fmt in self.allDateTimeFormats:
            try:
                return datetime.datetime.strptime(s, fmt)
            except ValueError:
                pass

        return None

#----------------------------------------------------------------------------

class NumericValidator(wx.PyValidator):
    """This validator only accepts numeric keys"""

    def __init__(self, acceptableChars="0123456789+-"):
        wx.PyValidator.__init__(self)
        self.Bind(wx.EVT_CHAR, self._OnChar)
        self.acceptableChars = acceptableChars
        self.acceptableCodes = [ord(x) for x in self.acceptableChars]
        stdEditKeys = [wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, wx.WXK_ESCAPE, wx.WXK_CANCEL,
                       wx.WXK_TAB, wx.WXK_BACK, wx.WXK_DELETE, wx.WXK_HOME, wx.WXK_END,
                       wx.WXK_LEFT, wx.WXK_RIGHT]
        self.acceptableCodes.extend(stdEditKeys)

    def Clone(self):
        "Make a new copy of this validator"
        return NumericValidator(self.acceptableChars)

    def _OnChar(self, event):
        "Handle the OnChar event by rejecting non-numerics"
        if event.GetModifiers() != 0 and event.GetModifiers() != wx.MOD_SHIFT:
            event.Skip()
            return

        if event.GetKeyCode() in self.acceptableCodes:
            event.Skip()
            return

        wx.Bell()

#----------------------------------------------------------------------------

class DateEditor(wx.DatePickerCtrl):
    """
    This control uses standard datetime.
    wx.DatePickerCtrl works only with wx.DateTime, but they are strange beasts.
    wx.DataTime use 0 indexed months, i.e. January==0 and December==11.
    """

    def __init__(self, *args, **kwargs):
        #kwargs["size"] = (0,0)
        wx.DatePickerCtrl.__init__(self, *args, **kwargs)
        self.SetValue(None)

    def SetValue(self, value):
        if value:
            dt = wx.DateTime()
            dt.Set(value.day, value.month-1, value.year)
        else:
            dt = wx.DateTime.Today()
        wx.DatePickerCtrl.SetValue(self, dt)

    def GetValue(self):
        "Get the value from the editor"
        dt = wx.DatePickerCtrl.GetValue(self)
        if dt.IsOk():
            return datetime.date(dt.Year, dt.Month+1, dt.Day)
        else:
            return None

#----------------------------------------------------------------------------

class TimeEditor(BaseCellTextEditor):
    """A text editor that expects and return time values"""

    # Acceptable formats: '23:59', '11:59pm', '11pm'
    STD_TIME_FORMATS = ['%X', '%H:%M', '%I:%M %p', '%I %p']

    def __init__(self, *args, **kwargs):
        BaseCellTextEditor.__init__(self, *args, **kwargs)
        self.formatString = "%X"

    def SetValue(self, value):
        "Put a new value into the editor"
        value = value or ""
        if isinstance(value, datetime.time):
            value = value.strftime(self.formatString)
        wx.TextCtrl.SetValue(self, value)

    def GetValue(self):
        "Get the value from the editor"
        s = wx.TextCtrl.GetValue(self).strip()
        fmts = self.STD_TIME_FORMATS[:]
        if self.formatString not in fmts:
            fmts.insert(0, self.formatString)
        for fmt in fmts:
            try:
                dt = datetime.datetime.strptime(s, fmt)
                return dt.time()
            except ValueError:
                pass

        return None

#======================================================================
# Auto complete controls

def MakeAutoCompleteTextBox(olv, columnIndex, maxObjectsToConsider=10000):
    """
    Return a TextCtrl that lets the user choose from all existing values in this column.
    Do not call for large lists
    """
    col = olv.columns[columnIndex]
    #THINK: We could make this time based, i.e. it escapes after 1 second.
    maxObjectsToConsider = min(maxObjectsToConsider, olv.GetItemCount())
    options = set(col.GetStringValue(olv.GetObjectAt(i)) for i in range(maxObjectsToConsider))
    tb = BaseCellTextEditor(olv, columnIndex)
    AutoCompleteHelper(tb, list(options))
    return tb

def MakeAutoCompleteComboBox(olv, columnIndex, maxObjectsToConsider=10000):
    """
    Return a ComboBox that lets the user choose from all existing values in this column.
    Do not call for large lists
    """
    col = olv.columns[columnIndex]
    maxObjectsToConsider = min(maxObjectsToConsider, olv.GetItemCount())
    options = set(col.GetStringValue(olv.GetObjectAt(i)) for i in range(maxObjectsToConsider))
    cb = wx.ComboBox(olv, choices=list(options),
                     style=wx.CB_DROPDOWN|wx.CB_SORT|wx.TE_PROCESS_ENTER)
    AutoCompleteHelper(cb)
    return cb


#-------------------------------------------------------------------------

class AutoCompleteHelper(object):
    """
    This class operates on a text control or combobox, and automatically completes the
    text typed by the user from a list of entries in a given list.

    """

    def __init__(self, control, possibleValues=None):
        self.control = control
        self.lastUserEnteredString = self.control.GetValue()
        self.control.Bind(wx.EVT_TEXT, self._OnTextEvent)
        if isinstance(self.control, wx.ComboBox):
            self.possibleValues = self.control.GetStrings()
        else:
            self.possibleValues = possibleValues or []
        self.lowerCasePossibleValues = [x.lower() for x in self.possibleValues]


    def _OnTextEvent(self, evt):
        evt.Skip()
        # After the SetValue() we want to ignore this event. If we get this event
        # and the value hasn't been modified, we know it was a SetValue() call.
        if hasattr(self.control, "IsModified") and not self.control.IsModified():
            return

        # If the text has changed more than the user just typing one letter,
        # then don't try to autocomplete it.
        if len(evt.GetString()) != len(self.lastUserEnteredString)+1:
            self.lastUserEnteredString = evt.GetString()
            return

        self.lastUserEnteredString = evt.GetString()
        s = evt.GetString().lower()
        for i, x in enumerate(self.lowerCasePossibleValues):
            if x.startswith(s):
                self._AutocompleteWith(self.possibleValues[i])
                break


    def _AutocompleteWith(self, newValue):
        """Suggest the given value by autocompleting it."""
        # GetInsertionPoint() doesn't seem reliable under linux
        insertIndex = len(self.control.GetValue())
        self.control.SetValue(newValue)
        if isinstance(self.control, wx.ComboBox):
            self.control.SetMark(insertIndex, len(newValue))
        else:
            # Seems that under linux, selecting only seems to work here if we do it
            # outside of the text event
            wx.CallAfter(self.control.SetSelection, insertIndex, len(newValue))
