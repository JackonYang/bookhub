import React, { PureComponent } from 'react';
// import PropTypes from 'prop-types';
import styles from './book-list.scss';
import bookDefault from '../../../assets/images/book-default.png';

const fake = () => {
  const max = 10;
  const data = [];
  for (let i = 0; i < max;) {
    data.push({
      ext: 'pdf',
      md5: '4fsaffdfad',
      path: '/Users/vivian/Music/',
      rawname: 'What are day',
      sizeBytes: 1611161,
      sizeReadable: '1.4 MB',
      lastRead: '24 Jan 2018',
      cover: '',
    });
    i += 1;
  }
  return data;
};
// const bookRender = ({ rawname, author = 'xxx', cover }) => (
//   <li>
//     <img alt={rawname} src={cover} />
//     <p className={styles.name}>rawname</p>
//     <p className={styles.author}>author</p>
//   </li>
// );

const bookRender = (book, idx) => (
  <li key={`${book.rawname}-${idx}`}>
    <img className={styles.img} alt={book.rawname} src={book.cover && book.cover !== '' ? book.cover : bookDefault} />
    <p className={styles.name}>{book.rawname}</p>
    <p className={styles.author}>{book.author && book.author.length > 0 ? book.author : 'Author'} </p>
  </li>
);

/* eslint-disable react/prefer-stateless-function */
class BookList extends PureComponent {
  // constructor(props) {
  //   super(props);
  //   // this.store = props.store;
  // }
  render() {
    const lis = fake().map((book, idx) => bookRender(book, idx));
    // const lis = this.store.getState().bookList.map(bookRender());
    return (
      <ul className={styles.books}>
        {lis}
      </ul>
    );
  }
}

// BookList.propTypes = {
//   store: PropTypes.shape({
//     dispatch: PropTypes.func.isRequired,
//     getState: PropTypes.func.isRequired,
//   }).isRequired,
// };

export default BookList;
