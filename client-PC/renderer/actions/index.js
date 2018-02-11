/*
 * action types
 */

export const BOOK_SCANNED = 'BOOK_SCANNED';
export const SELECT_ALL = 'SELECT_ALL';
export const SELECT_NONE = 'SELECT_NONE';
export const TOGGLE_SELECT = 'TOGGLE_SELECT';
export const TOGGLE_STAR = 'TOGGLE_STAR';

/*
 * action creators
 */

export function addBookMeta(metaInfo) {
  return { type: BOOK_SCANNED, metaInfo };
}

export function selectAll() {
  return { type: SELECT_ALL };
}

export function selectNone() {
  return { type: SELECT_NONE };
}

export function toggleStar(idx) {
  return { type: TOGGLE_STAR, idx };
}

export function toggleSelect(idx) {
  return { type: TOGGLE_SELECT, idx };
}
