import React from 'react';
import PropTypes from 'prop-types';
import styles from './table.scss';
// import radioIcon from '../../../assets/images/radio-icon.png';
// import radioIconChecked from '../../../assets/images/right.png';
import Trow from './trow/index';

// const FakeData = [
//   {
//     selected: false,
//     title: 'title',
//     author: 'author',
//     year: 'year',
//     type: 'type',
//     size: 'size',
//     createTime: 'createTime',
//     tags: ['aaa', 'bb'],
//   },
//   {
//     selected: true,
//     title: 'title2',
//     author: 'author',
//     year: 'year',
//     type: 'type',
//     size: 'size',
//     createTime: 'createTime',
//     tags: ['aaa', 'bb'],
//   },
//   {
//     selected: false,
//     title: 'title3',
//     author: 'author',
//     year: 'year',
//     type: 'type',
//     size: 'size',
//     createTime: 'createTime',
//     tags: ['aaa', 'bb'],
//   },
// ];

const thArrays = [
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
class Table extends React.Component {
  constructor(props) {
    super(props);
    this.store = props.store;
    this.state = {
      selectedList: [],
      // secondsElapsed: 0,
      // selectedAll: false,
      // deselectAll: false,
    };

    this.handleSelect = this.handleSelect.bind(this);
  }
  // componentWillMount() {
  //   console.log('componentWillMount');
  // }
  // componentDidMount() {
  //   // console.log('componentDidMount');
  //   this.interval = setInterval(this.tick.bind(this), 1000);
  // }
  // shouldComponentUpdate(nextProps, nextState) {
  //   // console.log('shouldComponentUpdate', nextProps, nextState, this.state.secondsElapsed);
  //   return this.state.secondsElapsed !== nextState.secondsElapsed;
  // }
  // componentWillUpdate() {
  //   console.log('componentWillUpdate');
  // }
  // componentWillUnmount() {
  //   clearInterval(this.interval);
  // }
  // tick() {
  //   // console.log(this.state);
  //   this.setState({ secondsElapsed: this.state.secondsElapsed + 1 });
  // }
  handleSelect(idx) {
    // console.log('handleSelect', idx);
    const tempList = [...this.state.selectedList];
    tempList[idx] = !tempList[idx];
    // tempList[idx] = typeof tempList[idxx] === 'undefined' ? true : !tempList[idx];
    this.setState({
      selectedList: [...tempList],
    });
    // console.log(this.state.selectedList);
  }
  render() {
    const ths = thArrays.map(th => <div className={styles.cell} key={th.file}>{th.text}</div>);
    ths.unshift(<div key="selecte" td-role="selecte" className={`${styles.cell} ${styles.selecte}`} />);
    // console.log('selectedList', this.state.selectedList);
    const trows = this.store.getState().scanLog.map((row, idx) => {
      console.log('idx', this.state.selectedList[idx]);
      return (<Trow
        key={row.md5}
        row={row}
        idx={idx}
        thArrays={thArrays}
        handleSelect={this.handleSelect}
        isSelected={!!this.state.selectedList[idx]}
      />);
    });

    return (
      <div className={styles.table} >
        <div className={`${styles.row} ${styles.header}`}>
          {ths}
        </div>
        {trows}
      </div>
    );
  }
}

/*  <div className={styles.row}>
  <div className={styles.cell}>
    Luke Peters
  </div>
  <div className={styles.cell}>
    25
  </div>
  <div className={styles.cell}>
    Freelance Web Developer
  </div>
  <div className={styles.cell}>
    Brookline, MA
  </div>
</div>
<div className={styles.row}>
  <div className={styles.cell}>
    Luke Peters
  </div>
  <div className={styles.cell}>
    25
  </div>
  <div className={styles.cell}>
    Freelance Web Developer
  </div>
  <div className={styles.cell}>
    Brookline, MA
  </div> */

Table.propTypes = {
  store: PropTypes.shape({
    dispatch: PropTypes.func.isRequired,
    getState: PropTypes.func.isRequired,
  }).isRequired,
};

export default Table;
