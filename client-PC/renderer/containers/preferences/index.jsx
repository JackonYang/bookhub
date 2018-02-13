import React from 'react';
import styles from './preferences.scss';

import FileIput from '../../components/file-input/index';
import Avatar from '../../components/avatar/index';

/* eslint-disable react/prefer-stateless-function */
class Preferences extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      library: null,
      monitors: [''],
      defaultText: 'user/book',
      isClearFiles: false,
    };
    this.handleLibraryChange = this.handleLibraryChange.bind(this);
    this.handleMonitorChange = this.handleMonitorChange.bind(this);
    this.handleAddMonitor = this.handleAddMonitor.bind(this);
    this.save = this.save.bind(this);
    this.cancel = this.cancel.bind(this);
  }
  // 当 自组件 FileInput 还原后，再将 isClearFiles 设为 false, 否则无法再次还原。
  /* eslint-disable react/no-did-update-set-state */
  componentDidUpdate(...rest) {
    if (rest[1].isClearFiles) {
      this.setState({ isClearFiles: false });
    }
  }
  handleLibraryChange(key) {
    if (key === this.state.library || key === '') return;
    this.setState({
      library: key,
    });
  }
  handleMonitorChange(key, i) {
    this.setState(({ monitors }) => ({
      monitors: [
        ...monitors.slice(0, i),
        key,
        ...monitors.slice(i + 1),
      ],
    }));
  }
  handleAddMonitor() {
    this.setState(preState => ({ monitors: [...preState.monitors, ''] }));
  }
  save() {
    console.log('save', this.state.monitors, this.state.library);
  }
  cancel() {
    this.setState({
      library: null,
      monitors: [''],
      isClearFiles: true,
    });
  }
  render() {
    const { monitors, defaultText, isClearFiles } = this.state;
    /* eslint-disable react/no-array-index-key  */
    /* eslint-disable react/jsx-no-bind  */
    const monitorEls = monitors.map((item, i) => <li key={`library-${i}`}><FileIput id={`library-${i}`} defaultText={defaultText} showAfter={false} onFileChangeCb={key => this.handleMonitorChange(key, i)} isClear={isClearFiles} /> </li>);
    return (
      <section className={styles.wrap}>
        <Avatar />
        <div className={styles.content}>
          <div className={styles.scrollContent}>
            <h1>
              Settings
            </h1>
            <div className={styles.libraryWrap}>
              <span className={styles.label}>Library Path</span>
              <FileIput id="library" defaultText={defaultText} showAfter={false} onFileChangeCb={this.handleLibraryChange} isClear={isClearFiles} />
            </div>
            <div className={styles.monitorWrap}>
              <span className={styles.label}>Monitor Path</span>
              <ul>
                { monitorEls }
              </ul>
              <span role="button" className={styles.add} onClick={this.handleAddMonitor} />
            </div>
          </div>
          <div className={styles.btnWrap}>
            <button className={styles.cancel} onClick={this.cancel}>取消</button>
            <button className={styles.save} onClick={this.save}>保存</button>
          </div>
        </div>
      </section>
    );
  }
}

export default Preferences;
