import React from 'react';
import PropTypes from 'prop-types';

import TopFixed from '../../components/top-fixed/index';
import BookList from '../../components/book-list/index';
import styles from './recently-read.scss';


const BtnsText = ['Author', 'Title', 'Tag'];

/* eslint-disable react/prefer-stateless-function */
class RecentRead extends React.Component {
  constructor(props) {
    super(props);
    this.store = props.store;
    this.state = {
      type: 'Author',
    };
    this.handleSwitchList = this.handleSwitchList.bind(this);
  }
  handleSwitchList(type) {
    console.log(`switch type: ${type}`);
    this.setState({ type });
  }
  render() {
    const btns = BtnsText.map(btn => <button key={btn} className={this.state.type === btn ? styles.active : ''} onClick={() => this.handleSwitchList(btn)} >{btn}</button>);
    return (
      <div className={styles.wrap}>
        <TopFixed type="book-search" />
        <div className={styles.contentWrap}>
          <h1>Recently Read</h1>
          <div className={styles.sortRole}>

            {btns}
          </div>
          <BookList />
        </div>
      </div>
    );
  }
}
RecentRead.propTypes = {
  store: PropTypes.shape({
    dispatch: PropTypes.func.isRequired,
    getState: PropTypes.func.isRequired,
  }).isRequired,
};

export default RecentRead;
