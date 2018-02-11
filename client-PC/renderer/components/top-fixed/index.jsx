import React from 'react';
import PropTypes from 'prop-types';

import styles from './top-fixed.scss';
import SearchInput from '../search-input/index';
import FileInput from '../file-input/index';

// https://github.com/electron/electron/issues/9920
const { ipcRenderer } = window.require('electron');


class TopFixed extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      // fileKey: 'user/图书文件夹',
      searchKey: '',
    };
    this.handleFileChange = this.handleFileChange.bind(this);
    this.handleSearchChange = this.handleSearchChange.bind(this);
  }

  handleFileChange(path) {
    // const fileKey = this.fileDom.files[0].path;
    ipcRenderer.send('scan:path:change', path);
    console.log(this);
    // this.setState({ fileKey: path });
  }

  handleSearchChange(key) {
    console.log(`key: ${key}`, `searchKey: ${this.state.searchKey}`);
    this.setState({ searchKey: key });
  }

  handleClose(e) {
    e.preventDefault();
    console.log('close', this);
  }

  render() {
    // 上传文件
    const fileInput = () => (
      <FileInput id="file-input" onFileChangeCb={this.handleFileChange} />
    );

    return (
      <div className={styles.wrap}>
        <button className={styles.close} onClick={this.handleClose} />
        {this.props.type === 'add' ? fileInput() : <SearchInput onSearchChangeCb={this.handleSearchChange} />}
      </div>
    );
  }
}

TopFixed.propTypes = {
  type: PropTypes.string,
};
TopFixed.defaultProps = {
  // 表示要展示 搜索(search) / 增加文件(add)
  type: 'add',
};
export default TopFixed;
