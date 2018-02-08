import {
  BOOK_SCANNED,
  SELECT_ALL,
  UNSELECT_ALL,
  TOGGLE_SELECT,
  TOGGLE_STAR,
} from '../actions';

const initialState = {
  bookList: [
    {
      ext: 'pdf',
      md5: '4fsaffdfad',
      path: '/Users/vivian/Music/',
      rawname: 'What are day',
      sizeBytes: 1611161,
      sizeReadable: '1.4 MB',
      lastRead: '24 Jan 2018',
    },
    {
      ext: 'pdf',
      md5: 'ddsadasd',
      path: '/Users/vivian/Music/',
      rawname: 'What ddsd day',
      sizeBytes: 1611162,
      sizeReadable: '1.58 MB',
      lastRead: '26 Oct 2017',
    },
  ],
  scanLog: [],
  selectedList: [],
  starList: [],
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
    case TOGGLE_STAR: {
      const tempStar = [...state.starList];
      tempStar[action.idx] = !tempStar[action.idx];

      return {
        ...state,
        starList: tempStar,
      };
    }
    default:
      return state;
  }
};
