import filesize from 'filesize';
import path from 'path';

import {
  BOOK_SCANNED,
  ADD_BOOK_TO_REPO,
  SELECT_ALL,
  SELECT_NONE,
  TOGGLE_SELECT,
  TOGGLE_STAR,
} from '../actions';

const initialState = {
  bookList: [],
  scanLog: [],
};

export default (state = initialState, action) => {
  switch (action.type) {
    case BOOK_SCANNED: {
      let updated = false;
      const newState = Object.assign({}, state, {
        scanLog: state.scanLog.map(bookMeta => {
          if (bookMeta.md5 === action.md5) {
            updated = true;
            return Object.assign({}, bookMeta, {
              srcFullPath: [
                action.srcFullPath,
                ...bookMeta.srcFullPath,
              ],
            });
          }
          return bookMeta;
        }),
      });

      if (!updated) {
        const {
          extname,
          srcFullPath,
          sizeBytes,
        } = action;

        // better algorithm. add titleAlias, standardTitle etc.
        const titleDisplay = path.basename(srcFullPath, extname);

        const sizeReadable = filesize(sizeBytes);

        newState.scanLog.push({
          md5: action.md5,
          titleDisplay,
          extname,
          sizeBytes,
          sizeReadable,
          // local info
          srcFullPath,
        });
      }
      return newState;
    }
    case ADD_BOOK_TO_REPO: {
      let updated = false;
      const newState = Object.assign({}, state, {
        bookList: state.bookList.map(bookMeta => {
          if (bookMeta.md5 === action.md5) {
            updated = true;
            return Object.assign({}, bookMeta, {
              srcFullPath: action.srcFullPath,
            });
          }
          return bookMeta;
        }),
      });

      if (!updated) {
        newState.bookList.push(action.bookMeta);
      }

      return newState;
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
