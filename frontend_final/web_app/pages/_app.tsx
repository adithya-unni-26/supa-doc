import React from 'react';
import { AppProps } from 'next/app';
import '../styles/globals.css';

const MyApp: React.FC<AppProps> = ({ Component, pageProps }) => {
  return (
    <div className="h-full bg-gray-100">
      <Component {...pageProps} />
    </div>
  );
};

export default MyApp;