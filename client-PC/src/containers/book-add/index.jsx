import React from 'react';
import TopFixed from '../../components/top-fixed/index';
import Table from '../../components/table/index';

/* eslint-disable react/prefer-stateless-function */
class BookAdd extends React.Component {
  render() {
    return (
      <div>
        <TopFixed type="add" />
        <h2>Here! Adding New Books</h2>
        <Table />
      </div>
    );
  }
}

export default BookAdd;
