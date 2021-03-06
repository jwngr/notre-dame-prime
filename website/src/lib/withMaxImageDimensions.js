import _ from 'lodash';
import React from 'react';

import {SIDEBAR_WIDTH_PX, IMAGE_BORDER_WIDTH_PX} from '../resources/constants';

export default (WrapperComponent) => {
  class MaxImageDimensionsComponent extends React.PureComponent {
    constructor(props) {
      super(props);

      this.debouncedResize = _.debounce(this.resize.bind(this), 350);

      window.addEventListener('resize', this.debouncedResize);

      this.state = {
        maxImageDimensions: {
          width: this.getMaxImageWidth(),
          height: this.getMaxImageHeight(),
        },
      };
    }

    componentWillUnmount() {
      window.removeEventListener('resize', this.debouncedResize);
    }

    resize() {
      this.setState({
        maxImageDimensions: {
          width: this.getMaxImageWidth(),
          height: this.getMaxImageHeight(),
        },
      });
    }

    getMaxImageWidth = () => {
      const windowWidth = window.innerWidth;
      const paddingWidth = 2 * 12;
      const borderWidth = 2 * IMAGE_BORDER_WIDTH_PX;

      let maximumImageWidth = windowWidth - paddingWidth - borderWidth;
      if (windowWidth > 768) {
        maximumImageWidth -= SIDEBAR_WIDTH_PX;
      }

      // Ensure the image width is never smaller than the width of the screen.
      let minimumImageWidth = window.screen.width - paddingWidth - borderWidth;

      return Math.max(maximumImageWidth, minimumImageWidth);
    };

    getMaxImageHeight = () => {
      const windowHeight = window.innerHeight;
      const paddingHeight = 2 * 12;
      const borderHeight = 2 * IMAGE_BORDER_WIDTH_PX;

      const maximumImageHeight = windowHeight - paddingHeight - borderHeight;

      // Ensure the image height is never smaller than the height of the screen.
      let minimumImageHeight = window.screen.height - paddingHeight - borderHeight;

      return Math.max(maximumImageHeight, minimumImageHeight);
    };

    render() {
      return <WrapperComponent {...this.state} {...this.props} />;
    }
  }

  return MaxImageDimensionsComponent;
};
