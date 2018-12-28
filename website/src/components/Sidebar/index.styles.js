import styled from 'styled-components';

export const SidebarWrapper = styled.div`
  width: 260px;
  height: 100vh;
  position: fixed;
  padding-left: 12px;
  padding-top: 20px;
`;

export const LogoWrapper = styled.div`
  margin-bottom: 28px;
`;

export const StepDetails = styled.div`
  flex: 1;
  display: flex;
  margin-top: -12px;
  margin-left: 32px;
  text-align: center;
  align-items: center;
  justify-content: center;
`;

export const SourceImage = styled.img`
  margin: auto;
  width: ${({width, height}) => (64 / height) * width}px;
  height: 64px;
`;

export const Swatch = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  opacity: 0.5;
  margin: 4px 8px;
  user-select: none;
  font-size: 8px;
`;
