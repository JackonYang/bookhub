import React from "react";
import ReactDOM from 'react-dom';

class BookList extends React.Component {
    render() {
      return (
        <h1>Here Is A List Of Books</h1>
        );
    }
}

ReactDOM.render(
    <BookList />,
    document.getElementById('content')
);
