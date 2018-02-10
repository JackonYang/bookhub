import React from 'react';
import PropTypes from 'prop-types';

import TopFixed from '../../components/top-fixed/index';
import Table from '../../components/table/index';
import styles from './book-search.scss';
// import { addBookMeta } from '../../actions';

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
    console.log('sss');
    return (
      <div className={styles.wrap}>
        <TopFixed type="search" />
        <div className={styles.contentWrap}>
          <Table type="search" {...this.props} />
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


export default BookSearch;
