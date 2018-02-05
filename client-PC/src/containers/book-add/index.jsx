import React from 'react';
import TopFixed from '../../components/top-fixed/index';
import Table from '../../components/table/index';
import styles from './book-add.scss';

// https://github.com/electron/electron/issues/9920
const { ipcRenderer } = window.require('electron');

/* eslint-disable react/prefer-stateless-function */
class BookAdd extends React.Component {
  componentDidMount() {
    ipcRenderer.on('scan:book:found', (e, metaInfo) => {
      console.log(metaInfo);
    });
  }

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
