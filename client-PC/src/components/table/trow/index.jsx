import React, { PureComponent } from 'react';
import PropTypes from 'prop-types';
import styles from './trow.scss';
import radioIcon from '../../../../assets/images/radio-icon.png';
import radioIconChecked from '../../../../assets/images/right.png';
import star from '../../../../assets/images/star@3x.png';
import starLighted from '../../../../assets/images/star-lighted@3x.png';


class Trow extends PureComponent {
  constructor(props) {
    super(props);
    this.state = {
    };
  }
/* eslint-disable */
  render() {
    const {
      row,
      thArrays,
      isSelected,
      idx,
      type,
    } = this.props;
    // 适配两种不同 type 的 row
    const darkSelect = type === 'search' ? star : radioIcon;
    const lightedSelect = type === 'search' ? starLighted : radioIconChecked;
    // console.log('render', isSelected);
      // console.log('render');
    const tds = thArrays.map((th, idx) => {
      console.log('tds', th, row[th.file]);
      return (
        <div
          className={styles.cell}
          key={row[th.file] || th.file + idx}
        >
          <span className={styles[th.file]}>{row[th.file]}</span>
        </div>
      );
    });

    /* eslint-disable function-paren-newline  */
    /* eslint-disable react/jsx-no-bind  */
    tds.unshift(
      <div
        key={`select-${idx}`}
        td-role="select"
        role="checkbox"
        onClick={() => this.props.handleSelect(idx)}
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
}
/* eslint-disable react/forbid-prop-types */
Trow.propTypes = {
  row: PropTypes.object.isRequired,
  type: PropTypes.oneOf(['add', 'search']).isRequired,
  idx: PropTypes.number.isRequired,
  thArrays: PropTypes.arrayOf(PropTypes.object).isRequired,
  isSelected: PropTypes.bool,
  handleSelect: PropTypes.func.isRequired,
};

Trow.defaultProps = {
  isSelected: true,
};

export default Trow;
