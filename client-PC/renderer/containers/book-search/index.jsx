import React from 'react';
import PropTypes from 'prop-types';
// import { connect } from 'react-redux';

import TopFixed from '../../components/top-fixed/index';
import Table from '../../components/table/index';
import styles from './book-search.scss';
// import { addBookMeta } from '../../actions';

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

/* eslint-disable react/prefer-stateless-function */
class BookSearch extends React.Component {
  constructor(props) {
    super(props);
    this.store = props.store;
  }
  searchMore() {
    console.log('searchMore', this);
  }
  render() {
    return (
      <div className={styles.wrap}>
        <TopFixed type="search" />
        <div className={styles.contentWrap}>
          <Table
            type="search"
            colTitles={colTitles}
            bookList={this.store.getState().bookList}
          />
        </div>
        <div className={styles.operationGrop}>
          <button className={styles.addHub} onClick={this.searchMore}>搜索更多</button>
        </div>
      </div>
    );
  }
}

BookSearch.propTypes = {
  store: PropTypes.shape({
    dispatch: PropTypes.func.isRequired,
    getState: PropTypes.func.isRequired,
  }).isRequired,
};

// const mapStateToProps = state => {
//   return { articles: state.articles };
// };

// const BookSearch = connect(mapStateToProps)(ConnectedBookSearch);

export default BookSearch;
