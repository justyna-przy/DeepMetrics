import { css } from 'styled-components';

/**
 * A simple frosted-glass CSS snippet.
 * Adjust background-color, blur strength, and border to your preference.
 */
export const frostedGlass = css`
  background-color: rgba(255, 255, 255, 0.02); 
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px); /* For Safari support */
  border: 1px solid rgba(255, 255, 255, 0.05);
`;
