import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { updateQuery } from 'actions';

import styles from './search-input.scss';

const mapStateToProps = state => ({
  query: state.query,
});

const mapDispatchToProps = dispatch => ({
  updateQuery: query => dispatch(updateQuery(query)),
});

function ConnectedSearchInput(props) {
  return (
    <label
      className={`${styles.inputWrap} ${styles.search}`}
      htmlFor="key-input"
    >
      <input
        id="key-input"
        type="text"
        value={props.query}
        onChange={event => props.updateQuery(event.target.value)}
      />
    </label>
  );
}

ConnectedSearchInput.propTypes = {
  query: PropTypes.string.isRequired,
  updateQuery: PropTypes.func.isRequired,
};

const SearchInput = connect(mapStateToProps, mapDispatchToProps)(ConnectedSearchInput);

export default SearchInput;
