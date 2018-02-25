import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import styles from './table.scss';
import Trow from './trow/index';

const mapStateToProps = (state, ownProps) => ({
  ...ownProps,
});

const mapDispatchToProps = () => ({
});

class ConnectedTable extends React.PureComponent {
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

    if (this.props.type === 'book-search') { // search 页面
      ths.unshift((<div
        key="star"
        td-role="star"
        className={`${styles.cell} ${styles.selecte}`}
      />));
    } else { // add 页面
      ths.unshift(<div
        key="selecte"
        td-role="selecte"
        className={`${styles.cell} ${styles.selecte}`}
      />);
    }

    trows = this.props.bookList.map((row, idx) => (<Trow
      key={row.md5}
      type={this.props.type}
      row={row}
      idx={idx}
      thArrays={this.props.colTitles}
    />));

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

ConnectedTable.propTypes = {
  type: PropTypes.oneOf(['add-book', 'book-search']).isRequired,
  colTitles: PropTypes.arrayOf(PropTypes.shape({
    text: PropTypes.string.isRequired,
    file: PropTypes.string.isRequired,
  })).isRequired,
  bookList: PropTypes.arrayOf(PropTypes.shape({
    md5: PropTypes.string.isRequired,
  })).isRequired,
};

const Table = connect(mapStateToProps, mapDispatchToProps)(ConnectedTable);

export default Table;
