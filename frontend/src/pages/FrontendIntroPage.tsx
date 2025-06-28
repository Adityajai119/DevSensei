import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import VideoModal from '../components/VideoModal';
import frontendVideo from '../assets/frontend.mp4';

const FrontendIntroPage: React.FC = () => {
  const [isVideoModalOpen, setIsVideoModalOpen] = useState(true);
  const navigate = useNavigate();

  const handleVideoEnded = () => {
    setIsVideoModalOpen(false);
    navigate('/frontend-playground');
  };

  return (
    <div className="min-h-screen bg-black">
      <VideoModal
        isOpen={isVideoModalOpen}
        onClose={handleVideoEnded}
        videoSrc={frontendVideo}
      />
    </div>
  );
};

export default FrontendIntroPage; 