import React from 'react';
// import PropTypes from 'prop-types';
import styles from './avatar.scss';
import AvatarPic from '../../assets/images/avatar.jpg';

/* eslint-disable react/prefer-stateless-function */
class Avatar extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
    };
  }
  render() {
    return (
      <div className={styles.wrap}>
        <img alt="头像" className={styles.avatar} src={AvatarPic} />
      </div>
    );
  }
}

// Avatar.propTypes = {
// };

// Avatar.defaultProps = {
// };
export default Avatar;
