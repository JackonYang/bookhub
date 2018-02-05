import React from 'react';
import TopFixed from '../../components/top-fixed/index';
import Table from '../../components/table/index';
import styles from './book-add.scss';

/* eslint-disable react/prefer-stateless-function */
class BookAdd extends React.Component {
  render() {
    return (
      <div className={styles.wrap}>
        <TopFixed type="add" />
        <div className={styles.contentWrap}>
          <Table />
        </div>
      </div>
    );
  }
}

export default BookAdd;
