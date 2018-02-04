import React from 'react';
import PropTypes from 'prop-types';
import styles from './index.scss';
import SearchInput from '../search-input/index';

class TopFixed extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      fileKey: 'user/图书文件夹',
      searchKey: '',
    };
    this.handleFileChange = this.handleFileChange.bind(this);
    this.handleSearchChange = this.handleSearchChange.bind(this);
  }

  handleFileChange() {
    this.setState({ fileKey: this.fileDom.files[0].path });
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
      <label className={`${styles.inputWrap} ${styles.file}`} htmlFor="file-input">
        <span className={styles.path}>{this.state.fileKey}</span>
        <input
          id="file-input"
          type="file"
          ref={input => {
            this.fileDom = input;
          }}
          onChange={this.handleFileChange}
          webkitdirectory="true"
          directory="true"
          multiple
        />
      </label>
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
