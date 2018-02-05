import React from 'react';
import PropTypes from 'prop-types';
import styles from './table.scss';
import radioIcon from '../../../assets/images/radio-icon.png';
// import radioIconChecked from '../../../assets/images/right.png';

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
  {
    text: 'MD5',
    file: 'md5',
  },
  // {
  //   text: 'Year',
  //   file: 'year',
  // },
  {
    text: 'Type',
    file: 'ext',
  },
  {
    text: 'Size',
    file: 'sizeReadable',
  },
  {
    text: 'Create Time',
    file: 'createTime',
  },
  {
    text: 'Tags',
    file: 'tags',
  },
];
class Table extends React.Component {
  constructor(props) {
    super(props);
    this.store = props.store;
  }

  render() {
    // console.log(this.state.data);
    const ths = thArrays.map(th => <div className={styles.cell} key={th.file}>{th.text}</div>);
    console.log('ths', ths);
    ths.unshift(<div key="operation" td-role="operation" className={`${styles.cell} ${styles.operation}`} />);

    const trows = this.store.getState().scanLog.map(row => {
      const tds = thArrays.map(th => {
        console.log(th);
        return <div className={styles.cell} key={row[th.file]}>{row[th.file]}</div>;
      });

      tds.unshift(<div key="operation" td-role="operation" className={`${styles.cell} ${styles.operation}`} ><img alt="radio" src={radioIcon} /> </div>);

      return (
        <div key={row.title} className={styles.row}>
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
