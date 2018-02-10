import React from 'react';
import PropTypes from 'prop-types';

import TopFixed from '../../components/top-fixed/index';
import BookList from '../../components/book-list/index';
import styles from './recent-read.scss';

/* eslint-disable react/prefer-stateless-function */
class RecentRead extends React.Component {
  constructor(props) {
    super(props);
    this.store = props.store;
  }
  render() {
    return (
      <div className={styles.wrap}>
        <TopFixed type="search" />
        <div className={styles.contentWrap}>
          <h1>Recently Read</h1>
          <div className={styles.sortRole}>
            <button>Author</button>
            <button>Title</button>
            <button>Tag</button>
          </div>
          <BookList />
        </div>
      </div>
    );
  }
}

RecentRead.propTypes = {
  store: PropTypes.shape({
    dispatch: PropTypes.func.isRequired,
    getState: PropTypes.func.isRequired,
  }).isRequired,
};

export default RecentRead;
