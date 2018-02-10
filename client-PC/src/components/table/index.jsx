import React from 'react';
import PropTypes from 'prop-types';
import styles from './table.scss';
// import radioIcon from '../../../assets/images/radio-icon.png';
// import radioIconChecked from '../../../assets/images/right.png';
import Trow from './trow/index';
import { toggleSelect, toggleStar } from '../../actions';


class Table extends React.Component {
  constructor(props) {
    super(props);
    this.store = props.store;
    this.state = {
      // selectedList: [],
      // secondsElapsed: 0,
      // selectedAll: false,
      // deselectAll: false,
    };

    this.handleSelect = this.handleSelect.bind(this);
    this.handleStar = this.handleStar.bind(this);
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

  // componentWillMount() {
  //   console.log('componentWillMount');
  //   console.log('isSelectAll', this.store.getState().isSelectAll);
  //   console.log('isUnSelectAll', this.store.getState().isUnSelectAll);
  // }
  // componentWillReceiveProps(nextProps) {
  //   console.log('componentWillReceiveProps');
  //   console.log(nextProps);
  //   console.log('isSelectAll', this.store.getState().isSelectAll,
  //   nextProps.store.getState().isSelectAll);
  //   console.log('isUnSelectAll', this.store.getState().isUnSelectAll,
  //   nextProps.store.getState().isUnSelectAll);
  // }

  handleSelect(idx) {
    console.log('handleSelect', idx);
    this.store.dispatch(toggleSelect(idx));
    // const tempList = [...this.state.selectedList];
    // tempList[idx] = !tempList[idx];
    // // tempList[idx] = typeof tempList[idxx] === 'undefined' ? true : !tempList[idx];
    // this.setState({
    //   selectedList: [...tempList],
    // });
    // console.log(this.state.selectedList);
  }
  handleStar(idx) {
    console.log('handleStar', idx);
    this.store.dispatch(toggleStar(idx));
    // const tempList = [...this.state.selectedList];
    // tempList[idx] = !tempList[idx];
    // // tempList[idx] = typeof tempList[idxx] === 'undefined' ? true : !tempList[idx];
    // this.setState({
    //   selectedList: [...tempList],
    // });
    // console.log(this.state.selectedList);
  }
  render() {
    let ths = [];
    let trows = [];
    // console.log('render', this.props.type, this.store.getState().bookList);

    ths = this.props.colTitles.map(th => (
      <div
        key={th.file}
        className={styles.cell}
      >
        {th.text}
      </div>
    ));

    if (this.props.type === 'search') {
      // search 页面
      ths.unshift(<div key="star" td-role="star" className={`${styles.cell} ${styles.selecte}`} />);
      const { starList } = this.store.getState();
      trows = this.store.getState().bookList.map((row, idx) => {
        console.log('idx', starList[idx]);
        return (<Trow
          key={row.md5}
          type="search"
          row={row}
          idx={idx}
          thArrays={this.props.colTitles}
          handleSelect={this.handleStar}
          isSelected={!!starList[idx]}
        />);
      });
    } else {
      // add 页面
      ths.unshift(<div key="selecte" td-role="selecte" className={`${styles.cell} ${styles.selecte}`} />);
      // console.log('selectedList', this.state.selectedList);
      const { selectedList } = this.store.getState();
      trows = this.store.getState().scanLog.map((row, idx) => {
        console.log('idx', selectedList[idx]);
        return (<Trow
          key={row.md5}
          row={row}
          idx={idx}
          thArrays={this.props.colTitles}
          handleSelect={this.handleSelect}
          isSelected={!!selectedList[idx]}
        />);
      });
    }
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
  // table 类型
  type: PropTypes.oneOf(['add', 'search']),
  colTitles: PropTypes.arrayOf(PropTypes.shape({
    text: PropTypes.string.isRequired,
    file: PropTypes.string.isRequired,
  })).isRequired,
};

Table.defaultProps = {
  type: 'add',
};

export default Table;
