import {
  BOOK_SCANNED,
} from '../actions';

const initialState = {
  bookList: [],
  scanLog: [],
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
    default:
      return state;
  }
};
