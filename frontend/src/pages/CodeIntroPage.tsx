import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import VideoModal from '../components/VideoModal';
import codeVideo from '../assets/code.mp4';

const CodeIntroPage: React.FC = () => {
  const [isVideoModalOpen, setIsVideoModalOpen] = useState(true);
  const navigate = useNavigate();

  const handleVideoEnded = () => {
    setIsVideoModalOpen(false);
    navigate('/code-playground');
  };

  return (
    <div className="min-h-screen bg-black">
      <VideoModal
        isOpen={isVideoModalOpen}
        onClose={handleVideoEnded}
        videoSrc={codeVideo}
      />
    </div>
  );
};

export default CodeIntroPage; 