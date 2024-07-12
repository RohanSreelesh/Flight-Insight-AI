import React, { useState, useEffect } from 'react';

const TypewriterEffect = ({ airlines, typingSpeed = 150, deletingSpeed = 50, pauseBetween = 2000 }) => {
  const [currentAirlineIndex, setCurrentAirlineIndex] = useState(0);
  const [currentText, setCurrentText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if(!airlines || airlines.length === 0){
      return;
    }
    
    const currentAirline = airlines[currentAirlineIndex];

    if (isDeleting) {
      if (currentText === '') {
        setIsDeleting(false);
        setCurrentAirlineIndex((prevIndex) => (prevIndex + 1) % airlines.length);
        return;
      }

      const timer = setTimeout(() => {
        setCurrentText((prevText) => prevText.slice(0, -1));
      }, deletingSpeed);
      return () => clearTimeout(timer);
    } else {
      if (currentText === currentAirline) {
        const timer = setTimeout(() => {
          setIsDeleting(true);
        }, pauseBetween);
        return () => clearTimeout(timer);
      }

      const timer = setTimeout(() => {
        setCurrentText((prevText) => currentAirline.slice(0, prevText.length + 1));
      }, typingSpeed);
      return () => clearTimeout(timer);
    }
  }, [currentAirlineIndex, currentText, isDeleting, airlines, typingSpeed, deletingSpeed, pauseBetween]);

  return <span className="text-blue-400">{currentText}</span>;
};

export default TypewriterEffect;