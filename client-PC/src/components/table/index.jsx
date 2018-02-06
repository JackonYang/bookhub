import React from 'react';
import PropTypes from 'prop-types';
import styles from './table.scss';
import radioIcon from '../../../assets/images/radio-icon.png';
import radioIconChecked from '../../../assets/images/right.png';

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
    };

    this.handleSelect = this.handleSelect.bind(this);
  }
  handleSelect(idx) {
    const tempList = [...this.state.selectedList];
    tempList[idx] = typeof tempList[idx] === 'undefined' ? true : !tempList[idx];
    this.setState({
      selectedList: [...tempList],
    });
    console.log(this.state.selectedList);
  }

  render() {
    // console.log(this.state.data);
    const ths = thArrays.map(th => <div className={styles.cell} key={th.file}>{th.text}</div>);
    // console.log('ths', ths);
    ths.unshift(<div key="selecte" td-role="selecte" className={`${styles.cell} ${styles.selecte}`} />);

    const trows = this.store.getState().scanLog.map((row, idx) => {
      const tds = thArrays.map(th => (
        <div
          className={styles.cell}
          key={row[th.file]}
        >
          <span className={styles[th.file]}>{row[th.file]}</span>
        </div>
      ));
      /* eslint-disable function-paren-newline  */
      /* eslint-disable react/jsx-no-bind  */
      tds.unshift(
        <div
          key="selecte"
          td-role="selecte"
          role="checkbox"
          onClick={() => this.handleSelect(idx)}
          className={`${styles.cell} ${styles.selecte}`}
        >
          <img alt="radio" src={this.state.selectedList[idx] ? radioIconChecked : radioIcon} />
        </div>);

      return (
        <div key={row.rawname} className={styles.row}>
          {tds}
        </div>
      );
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
// Table.propTypes = {
//   type: PropTypes.string,
// };
// Table.defaultProps = {
//   type: 'add',
// };

Table.propTypes = {
  store: PropTypes.shape({
    dispatch: PropTypes.func.isRequired,
    getState: PropTypes.func.isRequired,
  }).isRequired,
};

export default Table;
