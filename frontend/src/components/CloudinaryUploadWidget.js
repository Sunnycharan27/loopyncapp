import React, { useEffect } from 'react';

const CloudinaryUploadWidget = ({ onUploadSuccess, uploadPreset = 'loopync_unsigned', folder = 'loopync', resourceType = 'auto' }) => {
  const cloudName = process.env.REACT_APP_CLOUDINARY_CLOUD || 'demo';
  
  useEffect(() => {
    // Load Cloudinary widget script
    const script = document.createElement('script');
    script.src = 'https://upload-widget.cloudinary.com/global/all.js';
    script.async = true;
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  const openWidget = () => {
    if (window.cloudinary) {
      const widget = window.cloudinary.createUploadWidget(
        {
          cloudName,
          uploadPreset,
          folder,
          sources: ['local', 'camera'],
          resourceType,
          maxFileSize: resourceType === 'video' ? 50000000 : 10000000, // 50MB for videos, 10MB for images
          maxImageWidth: 2000,
          maxImageHeight: 2000,
          clientAllowedFormats: resourceType === 'video' ? ['mp4', 'mov', 'avi', 'webm'] : ['jpg', 'jpeg', 'png', 'gif', 'webp'],
          showPoweredBy: false,
          styles: {
            palette: {
              window: '#121427',
              sourceBg: '#0f021e',
              windowBorder: '#00E0FF',
              tabIcon: '#00E0FF',
              inactiveTabIcon: '#555',
              menuIcons: '#00E0FF',
              link: '#00E0FF',
              action: '#00E0FF',
              inProgress: '#00E0FF',
              complete: '#5AFF9C',
              error: '#FF3DB3',
              textDark: '#FFFFFF',
              textLight: '#FFFFFF'
            }
          }
        },
        (error, result) => {
          if (!error && result && result.event === 'success') {
            onUploadSuccess(result.info.secure_url, result.info);
          }
        }
      );
      widget.open();
    }
  };

  return { openWidget };
};

export default CloudinaryUploadWidget;
