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
  }
  handleFileChange() {
    const fileKey = this.fileDom.files[0].path;
    this.setState({ fileKey });
    this.props.onFileChangeCb(fileKey);
  }
  render() {
    return (
      <label className={`${styles.inputWrap} ${styles.file} ${this.props.showAfter ? styles.afterIcon : ''}`} htmlFor={this.props.id}>
        <span className={styles.path}>{this.state.fileKey}</span>
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
};

FileIput.defaultProps = {
  onFileChangeCb: () => {},
  id: 'file-input',
  showAfter: true,
};
export default FileIput;
