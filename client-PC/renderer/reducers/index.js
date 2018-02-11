import {
  BOOK_SCANNED,
  SELECT_ALL,
  SELECT_NONE,
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
      isStared: true,
    },
    {
      ext: 'pdf',
      md5: 'ddsadasd',
      path: '/Users/vivian/Music/',
      rawname: 'What ddsd day',
      sizeBytes: 1611162,
      sizeReadable: '1.58 MB',
      lastRead: '26 Oct 2017',
      isStared: false,
    },
  ],
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

    // Select for AddBooks Page
    case TOGGLE_SELECT: {
      return Object.assign({}, state, {
        scanLog: state.scanLog.map((bookMeta, idx) => {
          if (idx === action.idx) {
            return Object.assign({}, bookMeta, {
              isSelected: !bookMeta.isSelected,
            });
          }
          return bookMeta;
        }),
      });
    }
    case SELECT_ALL: {
      return Object.assign({}, state, {
        scanLog: state.scanLog.map(bookMeta => Object.assign({}, bookMeta, {
          isSelected: true,
        })),
      });
    }
    case SELECT_NONE: {
      return Object.assign({}, state, {
        scanLog: state.scanLog.map(bookMeta => Object.assign({}, bookMeta, {
          isSelected: false,
        })),
      });
    }

    case TOGGLE_STAR: {
      return Object.assign({}, state, {
        bookList: state.bookList.map((bookMeta, idx) => {
          if (idx === action.idx) {
            return Object.assign({}, bookMeta, {
              isStared: !bookMeta.isStared,
            });
          }
          return bookMeta;
        }),
      });
    }
    default:
      return state;
  }
};
