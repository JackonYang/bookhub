import React from 'react';
import styles from './preferences.scss';

/* eslint-disable react/prefer-stateless-function */
class Preferences extends React.Component {
  render() {
    return (
      <section className={styles.wrap}>
        <div className={styles.content}>
          <h1>
            Settings
          </h1>
          <div>
            <label htmlFor="library">Library Path</label>
            <input id="library" />
          </div>
        </div>
      </section>
    );
  }
}

export default Preferences;
