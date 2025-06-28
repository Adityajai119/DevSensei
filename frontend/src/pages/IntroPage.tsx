import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import VideoModal from '../components/VideoModal';
import repositoryVideo from '../assets/repository.mp4';

const IntroPage: React.FC = () => {
  const [isVideoModalOpen, setIsVideoModalOpen] = useState(true);
  const navigate = useNavigate();

  const handleVideoEnded = () => {
    setIsVideoModalOpen(false);
    navigate('/repository-explorer');
  };

  return (
    <div className="min-h-screen bg-black">
      <VideoModal
        isOpen={isVideoModalOpen}
        onClose={handleVideoEnded}
        videoSrc={repositoryVideo}
      />
    </div>
  );
};

export default IntroPage; 