import React from 'react';
import TopFixed from '../../components/top-fixed/index';

/* eslint-disable react/prefer-stateless-function */
class BookSearch extends React.Component {
  render() {
    return (
      <div>
        <TopFixed type="search" />
        <h2>Search And Read Books</h2>
      </div>
    );
  }
}

export default BookSearch;
