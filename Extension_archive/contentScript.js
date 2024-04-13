// Check if the API is available and if the user has granted permission
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    console.log('MediaDevices API available.');
  
    // Request access to the microphone
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(function(stream) {
        // Create an AudioContext
        const audioContext = new AudioContext();
        const source = audioContext.createMediaStreamSource(stream);
        const delay = audioContext.createDelay(5.0); // Max delay of 5 seconds
  
        // Set delay time (e.g., 3 seconds for testing)
        delay.delayTime.value = 3;
  
        // Connect the source to the delay, and the delay to the destination
        source.connect(delay);
        delay.connect(audioContext.destination);
  
        console.log('Echo delay setup complete.');
      })
      .catch(function(err) {
        console.error('Failed to get microphone access or set up audio:', err);
      });
  } else {
    console.error('MediaDevices API not available.');
  }
  