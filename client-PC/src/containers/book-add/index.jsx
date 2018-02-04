import React from 'react';
import TopFixed from '../../components/top-fixed/index';

/* eslint-disable react/prefer-stateless-function */
class BookAdd extends React.Component {
  render() {
    return (
      <div>
        <TopFixed type="add" />
        <h2>Here! Adding New Books</h2>
      </div>
    );
  }
}

export default BookAdd;
