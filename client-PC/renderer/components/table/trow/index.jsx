import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import utils from 'common/utils';
import { toggleSelect, toggleStar } from 'actions';

import radioIcon from 'assets/images/radio-icon.png';
import radioIconChecked from 'assets/images/right.png';
import star from 'assets/images/star@3x.png';
import starLighted from 'assets/images/star-lighted@3x.png';

import styles from './trow.scss';

const mapStateToProps = (state, ownProps) => ({
  ...ownProps,
});

const mapDispatchToProps = dispatch => ({
  toggleSelect: idx => dispatch(toggleSelect(idx)),
  toggleStar: idx => dispatch(toggleStar(idx)),
});

function ConnectedTableRow(props) {
  const {
    row,
    thArrays,
    idx,
    type,
  } = props;
  // 适配两种不同 type 的 row
  const darkSelect = type === 'book-search' ? star : radioIcon;
  const lightedSelect = type === 'book-search' ? starLighted : radioIconChecked;
  const isSelected = type === 'book-search' ? row.isStared : row.isSelected;
  const handleSelect = type === 'book-search' ? props.toggleStar : props.toggleSelect;

  const tds = thArrays.map((th, i) => (
    <div
      className={styles.cell}
      key={row[th.file] || th.file + i}
    >
      <span className={styles[th.file]}>
        {row[th.file]}
      </span>
    </div>
  ));

  /* eslint-disable function-paren-newline  */
  /* eslint-disable react/jsx-no-bind  */
  tds.unshift(
    <div
      key={`select-${row.md5}`}
      td-role="select"
      role="checkbox"
      onClick={() => handleSelect(idx)}
      className={`${styles.cell} ${styles.selecte}`}
    >
      <img alt="radio" src={isSelected ? lightedSelect : darkSelect} />
    </div>);

  return (
    <div
      key={row.md5}
      className={styles.row}
      onDoubleClick={utils.openFile(row.srcFullPath)}
    >
      {tds}
    </div>
  );
}

/* eslint-disable react/forbid-prop-types */
ConnectedTableRow.propTypes = {
  row: PropTypes.object.isRequired,
  type: PropTypes.oneOf(['add-book', 'book-search']).isRequired,
  idx: PropTypes.number.isRequired,
  thArrays: PropTypes.arrayOf(PropTypes.object).isRequired,
  toggleSelect: PropTypes.func.isRequired,
  toggleStar: PropTypes.func.isRequired,
};

const Trow = connect(mapStateToProps, mapDispatchToProps)(ConnectedTableRow);

export default Trow;
