import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import styles from './book-list.scss';
import bookDefault from '../../../assets/images/book-default.png';

const mapStateToProps = (state, ownProps) => ({
  bookList: state.bookList,
  ...ownProps,
});

const mapDispatchToProps = () => ({
});

const bookRender = (book, idx) => (
  <li key={`${book.rawname}-${idx}`}>
    <img className={styles.img} alt={book.rawname} src={book.cover && book.cover !== '' ? book.cover : bookDefault} />
    <p className={styles.name}>{book.titleDisplay}</p>
    <p className={styles.author}>{book.author && book.author.length > 0 ? book.author : 'Unknown Author'} </p>
  </li>
);

function ConnectedBookList(props) {
  const lis = props.bookList.map((book, idx) => bookRender(book, idx));
  // const lis = this.store.getState().bookList.map(bookRender());
  return (
    <ul className={styles.books}>
      {lis}
    </ul>
  );
}

ConnectedBookList.propTypes = {
  bookList: PropTypes.arrayOf(PropTypes.shape({
    md5: PropTypes.string.isRequired,
  })).isRequired,
};

const BookList = connect(mapStateToProps, mapDispatchToProps)(ConnectedBookList);

export default BookList;
