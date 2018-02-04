import React from 'react';
// import PropTypes from 'prop-types';
import styles from './index.scss';

const FakeData = [
  {
    selected: false,
    title: 'title',
    author: 'author',
    year: 'year',
    type: 'type',
    size: 'size',
    createTime: 'createTime',
    tags: ['aaa', 'bb'],
  },
  {
    selected: true,
    title: 'title2',
    author: 'author',
    year: 'year',
    type: 'type',
    size: 'size',
    createTime: 'createTime',
    tags: ['aaa', 'bb'],
  },
  {
    selected: false,
    title: 'title3',
    author: 'author',
    year: 'year',
    type: 'type',
    size: 'size',
    createTime: 'createTime',
    tags: ['aaa', 'bb'],
  },
];

const thArrays = [
  {
    text: 'Title',
    file: 'title',
  },
  {
    text: 'Author',
    file: 'author',
  },
  {
    text: 'Year',
    file: 'year',
  },
  {
    text: 'Type',
    file: 'type',
  },
  {
    text: 'Size',
    file: 'size',
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
    this.state = {
      data: FakeData,
    };
  }

  render() {
    console.log(this.state.data);
    const ths = thArrays.map(th => <div className={styles.cell} key={th.file}>{th.text}</div>);
    const trows = FakeData.map(row => {
      const tds = thArrays.map(th => {
        console.log(th);
        return <div className={styles.cell} key={row[th.file]}>{row[th.file]}</div>;
      });

      return (
        <div key={row.file} className={styles.row}>
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
export default Table;
