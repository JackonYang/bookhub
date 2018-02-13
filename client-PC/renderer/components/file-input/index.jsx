import React from 'react';
import PropTypes from 'prop-types';
import styles from './file-input.scss';

/* eslint-disable react/prefer-stateless-function */
class FileIput extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      fileKey: '',
    };
    this.handleFileChange = this.handleFileChange.bind(this);
    this.handleClear = this.handleClear.bind(this);
  }
  componentWillReceiveProps(nextProps) {
    if (nextProps.isClear !== this.props.isClear && nextProps.isClear) {
      this.setState({ fileKey: null });
    }
  }
  handleFileChange() {
    if (this.fileDom.files.length < 1) return;
    const fileKey = this.fileDom.files[0].path;
    this.setState({ fileKey });
    this.props.onFileChangeCb(fileKey);
  }
  // 父组件 isClear 为 true 时候执行，【取消键】
  handleClear() {
    this.setState({ fileKey: null });
  }
  render() {
    const { fileKey } = this.state;
    return (
      <label className={`${styles.inputWrap} ${styles.file} ${this.props.showAfter ? styles.afterIcon : ''}`} htmlFor={this.props.id}>
        <span className={styles.path}>{ (!fileKey || fileKey === '') ? this.props.defaultText : fileKey }</span>
        <input
          id={this.props.id}
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
  }
}

FileIput.propTypes = {
  onFileChangeCb: PropTypes.func,
  id: PropTypes.string,
  showAfter: PropTypes.bool,
  defaultText: PropTypes.string,
  isClear: PropTypes.bool,
};

FileIput.defaultProps = {
  onFileChangeCb: () => {},
  id: 'file-input',
  showAfter: true,
  defaultText: null,
  isClear: false,
};
export default FileIput;
