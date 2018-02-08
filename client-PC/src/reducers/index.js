import {
  BOOK_SCANNED,
  SELECT_ALL,
  UNSELECT_ALL,
  TOGGLE_SELECT,
} from '../actions';

const initialState = {
  bookList: [],
  scanLog: [],
  selectedList: [],
};

export default (state = initialState, action) => {
  switch (action.type) {
    case BOOK_SCANNED: {
      return Object.assign({}, state, {
        scanLog: [
          ...state.scanLog,
          action.metaInfo,
        ],
      });
    }
    case TOGGLE_SELECT: {
      const tempSelect = [...state.selectedList];
      tempSelect[action.idx] = !tempSelect[action.idx];

      return {
        ...state,
        selectedList: tempSelect,
      };
    }
    case SELECT_ALL: {
      const tempSelect = [];
      for (let i = 0; i < state.scanLog.length;) {
        if (!tempSelect[i]) tempSelect[i] = true;
        i += 1;
      }
      return {
        ...state,
        selectedList: tempSelect,
      };
    }
    case UNSELECT_ALL: {
      const tempSelect = [];
      for (let i = 0; i < state.scanLog.length;) {
        if (tempSelect[i]) tempSelect[i] = false;
        i += 1;
      }
      return {
        ...state,
        selectedList: tempSelect,
      };
    }
    default:
      return state;
  }
};
