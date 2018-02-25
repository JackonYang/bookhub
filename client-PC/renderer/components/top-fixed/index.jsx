import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import SearchInput from 'components/search-input/index';
import FileInput from 'components/file-input/index';

import styles from './top-fixed.scss';

// https://github.com/electron/electron/issues/9920
const { ipcRenderer } = window.require('electron');

const mapStateToProps = (state, ownProps) => ({
  bookList: state.bookList,
  ...ownProps,
});

const mapDispatchToProps = () => ({
});

function handleFileChange(path) {
  ipcRenderer.send('scan:task:new', path);
}

function handleClose(e) {
  e.preventDefault();
  window.location.assign('#/recently-read');
}

function ConnectedTopFixed(props) {
  // 上传文件
  const fileInput = () => (
    <FileInput id="file-input" onFileChangeCb={handleFileChange} />
  );

  return (
    <div className={styles.wrap}>
      {props.hasClose ? <button className={styles.close} onClick={handleClose} /> : null}
      {props.type === 'add-book' ? fileInput() : <SearchInput />}
    </div>
  );
}

ConnectedTopFixed.propTypes = {
  type: PropTypes.oneOf(['add-book', 'book-search']).isRequired,
  hasClose: PropTypes.bool,
};

ConnectedTopFixed.defaultProps = {
  hasClose: true,
};

const TopFixed = connect(mapStateToProps, mapDispatchToProps)(ConnectedTopFixed);

export default TopFixed;
