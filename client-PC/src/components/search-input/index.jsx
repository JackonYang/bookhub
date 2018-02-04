import React from 'react';
import PropTypes from 'prop-types';
import styles from './index.scss';

/* eslint-disable react/prefer-stateless-function */
class SearchIput extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      searchKey: '',
    };
    this.handleSearchChange = this.handleSearchChange.bind(this);
  }
  handleSearchChange(event) {
    this.setState({ searchKey: event.target.value });
    this.props.onSearchChangeCb(event.target.value);
  }
  render() {
    return (
      <label className={`${styles.inputWrap} ${styles.search}`} htmlFor="key-input">
        <input
          id="key-input"
          type="text"
          value={this.state.searchKey}
          onChange={this.handleSearchChange}
        />
      </label>
    );
  }
}

SearchIput.propTypes = {
  onSearchChangeCb: PropTypes.func,
};

SearchIput.defaultProps = {
  onSearchChangeCb: () => {},
};
export default SearchIput;
