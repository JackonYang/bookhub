import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import TopFixed from '../../components/top-fixed/index';
import Table from '../../components/table/index';
import styles from './book-add.scss';

import { addBookMeta, onUnSelectAll, onSelectAll } from '../../actions';

const mapStateToProps = (state, ownProps) => ({
  bookList: state.scanLog,
  ...ownProps,
});

const mapDispatchToProps = dispatch => ({
  selectAll: () => dispatch(onSelectAll()),
  selectNone: () => dispatch(onUnSelectAll()),
});

// https://github.com/electron/electron/issues/9920
const { ipcRenderer } = window.require('electron');

const colTitles = [
  {
    text: 'Title',
    file: 'rawname',
  },
  // {
  //   text: 'MD5',
  //   file: 'md5',
  // },
  // {
  //   text: 'Year',
  //   file: 'year',
  // },
  {
    text: 'Path',
    file: 'path',
  },
  // {
  //   text: 'Type',
  //   file: 'ext',
  // },
  {
    text: 'Size',
    file: 'sizeReadable',
  },
  // {
  //   text: 'Create Time',
  //   file: 'createTime',
  // },
  // {
  //   text: 'Tags',
  //   file: 'tags',
  // },
];

/* eslint-disable react/prefer-stateless-function */
class ConnectedBookAdd extends React.Component {
  constructor(props) {
    super(props);
    this.store = props.store;

    this.handleSelectAll = this.handleSelectAll.bind(this);
    this.handleDeselectAll = this.handleDeselectAll.bind(this);
  }
  componentDidMount() {
    ipcRenderer.on('scan:book:found', (e, metaInfo) => {
      // console.log(this.store.getState().scanLog.length);
      this.store.dispatch(addBookMeta(metaInfo));
    });
  }
  handleSelectAll() {
    console.log('selectall', this);
    this.store.dispatch(onSelectAll());
  }
  handleDeselectAll() {
    console.log('deselectall', this);
    this.store.dispatch(onUnSelectAll());
  }
  addToStore() {
    console.log('Add To Library', this);
  }
  render() {
    return (
      <div className={styles.wrap}>
        <TopFixed type="add" />
        <div className={styles.contentWrap}>
          <Table
            type="add"
            colTitles={colTitles}
            bookList={this.props.bookList}
          />
        </div>
        <div className={styles.operationGrop}>
          <div className={styles.leftBtnGrop}>
            <span role="button" className={styles.selectBtn} onClick={this.handleSelectAll}>All</span>
            <span role="button" className={styles.selectBtn} onClick={this.handleDeselectAll}>None</span>
          </div>
          <button className={styles.addHub} onClick={this.addToStore}>Add To Library</button>
        </div>
      </div>
    );
  }
}

ConnectedBookAdd.propTypes = {
  store: PropTypes.shape({
    dispatch: PropTypes.func.isRequired,
    getState: PropTypes.func.isRequired,
  }).isRequired,
  bookList: PropTypes.arrayOf(PropTypes.shape({
    md5: PropTypes.string.isRequired,
    ext: PropTypes.string.isRequired,
  })).isRequired,
};

const BookAdd = connect(mapStateToProps, mapDispatchToProps)(ConnectedBookAdd);

export default BookAdd;
