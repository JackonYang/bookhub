import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import TopFixed from '../../components/top-fixed/index';
import Table from '../../components/table/index';
import styles from './book-search.scss';
// import { addBookMeta } from '../../actions';

const mapStateToProps = (state, ownProps) => ({
  bookList: state.bookList,
  ...ownProps,
});

const mapDispatchToProps = () => ({
});

const colTitles = [
  {
    text: 'Title',
    file: 'titleDisplay',
  },
  {
    text: 'Author',
    file: 'author',
  },
  {
    text: 'Type',
    file: 'extname',
  },
  {
    text: 'Last Read',
    file: 'lastRead',
  },
  // {
  //   text: 'Tags',
  //   file: 'tags',
  // },
];

function searchMore() {
  console.log('searchMore');
}

/* eslint-disable react/prefer-stateless-function */
function ConnectedBookSearch(props) {
  return (
    <div className={styles.wrap}>
      <TopFixed type="search" />
      <div className={styles.contentWrap}>
        <Table
          type="search"
          colTitles={colTitles}
          bookList={props.bookList}
        />
      </div>
      <div className={styles.operationGrop}>
        <button className={styles.addHub} onClick={searchMore}>Search More</button>
      </div>
    </div>
  );
}

ConnectedBookSearch.propTypes = {
  bookList: PropTypes.arrayOf(PropTypes.shape({
    md5: PropTypes.string.isRequired,
  })).isRequired,
};

// const mapStateToProps = state => {
//   return { articles: state.articles };
// };

const BookSearch = connect(mapStateToProps, mapDispatchToProps)(ConnectedBookSearch);

export default BookSearch;
