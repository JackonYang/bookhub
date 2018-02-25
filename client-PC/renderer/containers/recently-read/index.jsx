import React from 'react';
// import PropTypes from 'prop-types';

import TopFixed from 'components/top-fixed/index';
import BookList from 'components/book-list/index';
import Avatar from 'components/avatar/index';

import styles from './recently-read.scss';

// const BtnsText = ['Author', 'Title', 'Tag'];

// handleSwitchList(type) {
//   console.log(`switch type: ${type}`);
//   this.setState({ type });
// }

function RecentRead() {
  // const btns = BtnsText.map(btn => (
  //   <button
  //     key={btn}
  //     className={this.state.type === btn ? styles.active : ''}
  //     onClick={() => this.handleSwitchList(btn)}
  //   >
  //     {btn}
  //   </button>
  // ));
  return (
    <div className={styles.wrap}>
      <Avatar />
      <TopFixed type="book-search" hasClose={false} />
      <div className={styles.contentWrap}>
        <h1>Recently Read</h1>
        {/* <div className={styles.sortRole}>
            {btns}
          </div> */}
        <BookList />
      </div>
    </div>
  );
}

export default RecentRead;
