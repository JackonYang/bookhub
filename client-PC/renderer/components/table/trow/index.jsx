import React from 'react';
import PropTypes from 'prop-types';
import styles from './trow.scss';
import radioIcon from '../../../../assets/images/radio-icon.png';
import radioIconChecked from '../../../../assets/images/right.png';
import star from '../../../../assets/images/star@3x.png';
import starLighted from '../../../../assets/images/star-lighted@3x.png';


function Trow(props) {
  const {
    row,
    thArrays,
    idx,
    type,
  } = props;
  // 适配两种不同 type 的 row
  const darkSelect = type === 'search' ? star : radioIcon;
  const lightedSelect = type === 'search' ? starLighted : radioIconChecked;
  const isSelected = type === 'search' ? row.isStared : row.isSelected;

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
      key={`select-${idx}`}
      td-role="select"
      role="checkbox"
      onClick={() => props.handleSelect(idx)}
      className={`${styles.cell} ${styles.selecte}`}
    >
      <img alt="radio" src={isSelected ? lightedSelect : darkSelect} />
    </div>);

  return (
    <div className={styles.row}>
      {tds}
    </div>
  );
}

/* eslint-disable react/forbid-prop-types */
Trow.propTypes = {
  row: PropTypes.object.isRequired,
  type: PropTypes.oneOf(['add', 'search']).isRequired,
  idx: PropTypes.number.isRequired,
  thArrays: PropTypes.arrayOf(PropTypes.object).isRequired,
  handleSelect: PropTypes.func.isRequired,
};

export default Trow;
