# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Name:         OLVEvent.py
# Author:       Phillip Piper
# Created:      3 April 2008
# SVN-ID:       $Id$
# Copyright:    (c) 2008 by Phillip Piper, 2008
# License:      wxWindows license
#----------------------------------------------------------------------------
# Change log:
# 2008/08/18  JPP   Added CELL_EDIT_STARTED and CELL_EDIT_FINISHED events
# 2008/07/16  JPP   Added group-related events
# 2008/06/19  JPP   Added EVT_SORT
# 2008/05/26  JPP   Fixed pyLint annoyances
# 2008/04/04  JPP   Initial version complete
#----------------------------------------------------------------------------
# To do:

"""
The OLVEvent module holds all the events used by the ObjectListView module.
"""

__author__ = "Phillip Piper"
__date__ = "3 August 2008"
__version__ = "1.1"

import wx

#======================================================================
# Event ids and types

def _EventMaker():
    evt = wx.NewEventType()
    return (evt, wx.PyEventBinder(evt))

(olv_EVT_CELL_EDIT_STARTING, EVT_CELL_EDIT_STARTING) = _EventMaker()
(olv_EVT_CELL_EDIT_STARTED, EVT_CELL_EDIT_STARTED) = _EventMaker()
(olv_EVT_CELL_EDIT_FINISHING, EVT_CELL_EDIT_FINISHING) = _EventMaker()
(olv_EVT_CELL_EDIT_FINISHED, EVT_CELL_EDIT_FINISHED) = _EventMaker()
(olv_EVT_SORT, EVT_SORT) = _EventMaker()
(olv_EVT_GROUP_CREATING, EVT_GROUP_CREATING) = _EventMaker()
(olv_EVT_GROUP_SORT, EVT_GROUP_SORT) = _EventMaker()
(olv_EVT_EXPANDING, EVT_EXPANDING) = _EventMaker()
(olv_EVT_EXPANDED, EVT_EXPANDED) = _EventMaker()
(olv_EVT_COLLAPSING, EVT_COLLAPSING) = _EventMaker()
(olv_EVT_COLLAPSED, EVT_COLLAPSED) = _EventMaker()

#======================================================================
# Event parameter blocks

class VetoableEvent(wx.PyCommandEvent):
    """
    Base class for all cancellable actions
    """

    def __init__(self, evtType):
        wx.PyCommandEvent.__init__(self, evtType, -1)
        self.veto = False

    def Veto(self, isVetoed=True):
        """
        Veto (or un-veto) this event
        """
        self.veto = isVetoed

    def IsVetoed(self):
        """
        Has this event been vetod?
        """
        return self.veto

#----------------------------------------------------------------------------

class CellEditEvent(VetoableEvent):
    """
    Base class for all cell editing events
    """

    def SetParameters(self, objectListView, rowIndex, subItemIndex, rowModel, cellValue, editor):
        self.objectListView = objectListView
        self.rowIndex = rowIndex
        self.subItemIndex = subItemIndex
        self.rowModel = rowModel
        self.cellValue = cellValue
        self.editor = editor

#----------------------------------------------------------------------------

class CellEditStartedEvent(CellEditEvent):
    """
    A cell has started to be edited.

    All attributes are public and should be considered read-only.
    """

    def __init__(self, objectListView, rowIndex, subItemIndex, rowModel, cellValue, cellBounds, editor):
        CellEditEvent.__init__(self, olv_EVT_CELL_EDIT_STARTED)
        self.SetParameters(objectListView, rowIndex, subItemIndex, rowModel, cellValue, editor)
        self.cellBounds = cellBounds

#----------------------------------------------------------------------------

class CellEditStartingEvent(CellEditEvent):
    """
    A cell is about to be edited.

    All attributes are public and should be considered read-only. Methods are provided for
    information that can be changed.
    """

    def __init__(self, objectListView, rowIndex, subItemIndex, rowModel, cellValue, cellBounds, editor):
        CellEditEvent.__init__(self, olv_EVT_CELL_EDIT_STARTING)
        self.SetParameters(objectListView, rowIndex, subItemIndex, rowModel, cellValue, editor)
        self.cellBounds = cellBounds
        self.newEditor = None
        self.shouldConfigureEditor = True

    def SetCellBounds(self, rect):
        """
        Change where the editor will be placed.
        rect is a list: [left, top, width, height]
        """
        self.cellBounds = rect

    def SetNewEditor(self, control):
        """
        Use the given control instead of the editor.
        """
        self.newEditor = control

    def DontConfigureEditor(self):
        """
        The editor will not be automatically configured.

        If this is called, the event handler must handle all configuration. In
        particular, it must configure its own event handlers to that
        ObjectListView.CancelCellEdit() is called when the user presses Escape,
        and ObjectListView.CommitCellEdit() is called when the user presses
        Enter/Return or when the editor loses focus. """
        self.shouldConfigureEditor = False

#----------------------------------------------------------------------------

class CellEditFinishedEvent(CellEditEvent):
    """
    The user has finished editing a cell.
    """
    def __init__(self, objectListView, rowIndex, subItemIndex, rowModel, userCancelled):
        CellEditEvent.__init__(self, olv_EVT_CELL_EDIT_FINISHED)
        self.SetParameters(objectListView, rowIndex, subItemIndex, rowModel, None, None)
        self.userCancelled = userCancelled

#----------------------------------------------------------------------------

class CellEditFinishingEvent(CellEditEvent):
    """
    The user is finishing editing a cell.

    If this event is vetoed, the edit will be cancelled silently. This is useful if the
    event handler completely handles the model updating.
    """
    def __init__(self, objectListView, rowIndex, subItemIndex, rowModel, cellValue, editor, userCancelled):
        CellEditEvent.__init__(self, olv_EVT_CELL_EDIT_FINISHING)
        self.SetParameters(objectListView, rowIndex, subItemIndex, rowModel, cellValue, editor)
        self.userCancelled = userCancelled

    def SetCellValue(self, value):
        """
        If the event handler sets the cell value here, this value will be used to update the model
        object, rather than the value that was actually in the cell editor
        """
        self.cellValue = value

#----------------------------------------------------------------------------

class SortEvent(VetoableEvent):
    """
    The user wants to sort the ObjectListView.

    When sortModelObjects is True, the event handler should sort the model objects used by
    the given ObjectListView. If the "modelObjects" instance variable is not None, that
    collection of objects should be sorted, otherwise the "modelObjects" collection of the
    ObjectListView should be sorted. For a VirtualObjectListView, "modelObjects" will
    always be None and the programmer must sort the object in whatever backing store is
    being used.

    When sortModelObjects is False, the event handler must sort the actual ListItems in
    the OLV. It does this by calling SortListItemsBy(), passing a callable that accepts
    two model objects as parameters. sortModelObjects must be True for a
    VirtualObjectListView (or a FastObjectListView) since virtual lists cannot sort items.

    If the handler calls Veto(), no further default processing will be done.
    If the handler calls Handled(), default processing concerned with UI will be done. This
    includes updating sort indicators.
    If the handler calls neither of these, all default processing will be done.
    """
    def __init__(self, objectListView, sortColumnIndex, sortAscending, sortModelObjects, modelObjects=None):
        VetoableEvent.__init__(self, olv_EVT_SORT)
        self.objectListView = objectListView
        self.sortColumnIndex = sortColumnIndex
        self.sortAscending = sortAscending
        self.sortModelObjects = sortModelObjects
        self.modelObjects = modelObjects
        self.wasHandled = False

    def Handled(self, wasHandled=True):
        """
        Indicate that the event handler has sorted the ObjectListView.
        The OLV will handle other tasks like updating sort indicators
        """
        self.wasHandled = wasHandled

#----------------------------------------------------------------------------

class GroupCreationEvent(wx.PyCommandEvent):
    """
    The user is about to create one or more groups.

    The handler can mess with the list of groups before they are created: change their
    names, give them icons, remove them from the list to stop them being created
    (that last behaviour could be very confusing for the users).
    """
    def __init__(self, objectListView, groups):
        wx.PyCommandEvent.__init__(self, olv_EVT_GROUP_CREATING, -1)
        self.objectListView = objectListView
        self.groups = groups

#----------------------------------------------------------------------------

class ExpandCollapseEvent(VetoableEvent):
    """
    The user wants to expand or collapse one or more groups, or has just done so.

    If the handler calls Veto() for a Expanding or Collapsing event,
    the expand/collapse action will be cancelled.

    Calling Veto() has no effect on a Expanded or Collapsed event
    """
    def __init__(self, eventType, objectListView, groups, isExpand):
        VetoableEvent.__init__(self, eventType)
        self.objectListView = objectListView
        self.groups = groups
        self.isExpand = isExpand

def ExpandingCollapsingEvent(objectListView, groups, isExpand):
    if isExpand:
        return ExpandCollapseEvent(olv_EVT_EXPANDING, objectListView, groups, True)
    else:
        return ExpandCollapseEvent(olv_EVT_COLLAPSING, objectListView, groups, False)

def ExpandedCollapsedEvent(objectListView, groups, isExpand):
    if isExpand:
        return ExpandCollapseEvent(olv_EVT_EXPANDED, objectListView, groups, True)
    else:
        return ExpandCollapseEvent(olv_EVT_COLLAPSED, objectListView, groups, False)

#----------------------------------------------------------------------------

class SortGroupsEvent(wx.PyCommandEvent):
    """
    The given list of groups needs to be sorted.

    Both the groups themselves and the model objects within the group should be sorted.

    The handler should rearrange the list of groups in the order desired.
    """
    def __init__(self, objectListView, groups, sortColumn, sortAscending):
        wx.PyCommandEvent.__init__(self, olv_EVT_GROUP_SORT, -1)
        self.objectListView = objectListView
        self.groups = groups
        self.sortColumn = sortColumn
        self.sortAscending = sortAscending
        self.wasHandled = False

    def Handled(self, wasHandled=True):
        """
        Indicate that the event handler has sorted the groups.
        """
        self.wasHandled = wasHandled
