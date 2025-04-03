document.addEventListener('DOMContentLoaded', () => {
    // DOM elements
    const videoElement = document.getElementById('webcam');
    const canvasElement = document.getElementById('canvas');
    const canvasCtx = canvasElement.getContext('2d');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const exerciseSelect = document.getElementById('exercise-select');
    const statusLabel = document.getElementById('status-label');
    const scoreLabel = document.getElementById('score-label');
    const timeLabel = document.getElementById('time-label');
    const instructionsText = document.getElementById('instructions-text');
    
    // App state
    let isRunning = false;
    let stream = null;
    let animationId = null;
    
    // Load initial instructions
    updateInstructions(exerciseSelect.value);
    
    // Event listeners
    exerciseSelect.addEventListener('change', () => {
        updateInstructions(exerciseSelect.value);
    });
    
    startBtn.addEventListener('click', startExercise);
    stopBtn.addEventListener('click', stopExercise);
    
    // Initialize webcam
    async function initWebcam() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: 640,
                    height: 480,
                    facingMode: 'user'
                }
            });
            videoElement.srcObject = stream;
            return true;
        } catch (error) {
            console.error('Error accessing webcam:', error);
            alert('Error accessing webcam. Please make sure you have granted camera permissions.');
            return false;
        }
    }
    
    // Initialize webcam on page load
    initWebcam();
    
    async function updateInstructions(exerciseName) {
        try {
            const response = await fetch(`/api/instructions/${encodeURIComponent(exerciseName)}`);
            const data = await response.json();
            instructionsText.textContent = data.instructions;
        } catch (error) {
            console.error('Error fetching instructions:', error);
            instructionsText.textContent = 'Failed to load instructions.';
        }
    }
    
    async function startExercise() {
        if (isRunning) return;
        
        if (!stream) {
            const success = await initWebcam();
            if (!success) return;
        }
        
        const exercise = exerciseSelect.value;
        
        try {
            const response = await fetch('/api/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ exercise })
            });
            
            const data = await response.json();
            
            if (data.status === 'started') {
                isRunning = true;
                statusLabel.textContent = 'Analyzing...';
                statusLabel.style.color = 'blue';
                scoreLabel.textContent = '0';
                timeLabel.textContent = '0s';
                
                // Start processing frames
                processFrame();
            }
        } catch (error) {
            console.error('Error starting exercise:', error);
            alert('Error starting exercise. Please try again.');
        }
    }
    
    async function stopExercise() {
        if (!isRunning) return;
        
        try {
            const response = await fetch('/api/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.status === 'stopped') {
                isRunning = false;
                statusLabel.textContent = 'Stopped';
                statusLabel.style.color = 'gray';
                
                if (animationId) {
                    cancelAnimationFrame(animationId);
                    animationId = null;
                }
                
                // Show final results
                alert(`Exercise completed!\nFinal score: ${data.final_score}\nTime: ${data.time} seconds`);
            }
        } catch (error) {
            console.error('Error stopping exercise:', error);
            alert('Error stopping exercise. Please try again.');
        }
    }
    
    async function processFrame() {
        if (!isRunning) return;
        
        // Draw video frame to canvas
        canvasElement.width = videoElement.videoWidth;
        canvasElement.height = videoElement.videoHeight;
        canvasCtx.drawImage(videoElement, 0, 0);
        
        // Get canvas data as base64 image
        const imageData = canvasElement.toDataURL('image/jpeg', 0.8);
        
        try {
            const response = await fetch('/api/process_frame', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ image: imageData })
            });
            
            const data = await response.json();
            
            // Update canvas with processed image
            const img = new Image();
            img.onload = function() {
                canvasCtx.drawImage(img, 0, 0);
                
                // Update status display
                const status = data.status;
                statusLabel.textContent = status.status;
                statusLabel.style.color = status.status.includes('Correct') ? 'green' : 'red';
                scoreLabel.textContent = status.score;
                timeLabel.textContent = `${status.time}s`;
                
                // Continue processing frames
                animationId = requestAnimationFrame(processFrame);
            };
            img.src = data.image;
        } catch (error) {
            console.error('Error processing frame:', error);
            animationId = requestAnimationFrame(processFrame);
        }
    }
});
