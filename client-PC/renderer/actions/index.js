/*
 * action types
 */

export const BOOK_SCANNED = 'BOOK_SCANNED';
export const SELECT_ALL = 'SELECT_ALL';
export const UNSELECT_ALL = 'UNSELECT_ALL';
export const TOGGLE_SELECT = 'TOGGLE_SELECT';
export const TOGGLE_STAR = 'TOGGLE_STAR';

/*
 * action creators
 */

export function addBookMeta(metaInfo) {
  return { type: BOOK_SCANNED, metaInfo };
}

export function toggleSelect(idx) {
  return { type: TOGGLE_SELECT, idx };
}

export function onSelectAll() {
  return { type: SELECT_ALL };
}

export function onUnSelectAll() {
  return { type: UNSELECT_ALL };
}

export function toggleStar(idx) {
  return { type: TOGGLE_STAR, idx };
}
