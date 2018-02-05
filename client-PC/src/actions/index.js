/*
 * action types
 */

export const BOOK_SCANNED = 'BOOK_SCANNED';

/*
 * action creators
 */

export function addBookMeta(metaInfo) {
  return { type: BOOK_SCANNED, metaInfo };
}
