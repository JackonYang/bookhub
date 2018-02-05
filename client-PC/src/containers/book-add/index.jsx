import React from 'react';
import PropTypes from 'prop-types';

import TopFixed from '../../components/top-fixed/index';
import Table from '../../components/table/index';
import styles from './book-add.scss';

import { addBookMeta } from '../../actions';


// https://github.com/electron/electron/issues/9920
const { ipcRenderer } = window.require('electron');

/* eslint-disable react/prefer-stateless-function */
class BookAdd extends React.Component {
  constructor(props) {
    super(props);
    this.store = props.store;
  }
  componentDidMount() {
    ipcRenderer.on('scan:book:found', (e, metaInfo) => {
      // console.log(this.store.getState().scanLog.length);
      this.store.dispatch(addBookMeta(metaInfo));
    });
  }

  render() {
    return (
      <div className={styles.wrap}>
        <TopFixed type="add" />
        <div className={styles.contentWrap}>
          <Table {...this.props} />
        </div>
      </div>
    );
  }
}

BookAdd.propTypes = {
  store: PropTypes.shape({
    dispatch: PropTypes.func.isRequired,
    getState: PropTypes.func.isRequired,
  }).isRequired,
};

export default BookAdd;
