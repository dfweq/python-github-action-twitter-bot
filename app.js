document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const startRecordingBtn = document.getElementById('startRecording');
    const stopRecordingBtn = document.getElementById('stopRecording');
    const audioFileInput = document.getElementById('audioFileInput');
    const recordingStatus = document.getElementById('recordingStatus');
    const recordingTime = document.getElementById('recordingTime');
    const fileName = document.getElementById('fileName');
    const audioPreview = document.getElementById('audioPreview');
    const audioPlayer = document.getElementById('audioPlayer');
    const submitAudioBtn = document.getElementById('submitAudio');
    const statusContainer = document.getElementById('status-container');
    const processingStatus = document.getElementById('processingStatus');
    const progressBar = document.getElementById('progressBar');

    // MediaRecorder variables
    let mediaRecorder;
    let audioChunks = [];
    let recordingTimer;
    let recordingSeconds = 0;
    let audioBlob;
    let audioFile;

    // Check if MediaRecorder is supported
    if (!window.MediaRecorder) {
        alert('Your browser does not support audio recording. Please try a different browser or upload a voice memo instead.');
        startRecordingBtn.disabled = true;
    }

    // Start recording function
    startRecordingBtn.addEventListener('click', async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Reset recording state
            audioChunks = [];
            recordingSeconds = 0;
            updateRecordingTime();
            
            // Start recording
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };
            
            mediaRecorder.onstop = () => {
                // Create blob from recorded chunks
                audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                
                // Create a playable URL and set it to audio player
                const audioUrl = URL.createObjectURL(audioBlob);
                audioPlayer.src = audioUrl;
                
                // Update UI for preview and submission
                audioPreview.classList.remove('hidden');
                fileName.textContent = "Recorded audio ready for submission";
                
                // Convert to File object for later use
                audioFile = new File([audioBlob], "recording.webm", { 
                    type: "audio/webm"
                });
                
                // Stop all tracks from the stream to release microphone
                stream.getTracks().forEach(track => track.stop());
            };
            
            // Start the recording
            mediaRecorder.start();
            
            // Update UI
            startRecordingBtn.disabled = true;
            stopRecordingBtn.disabled = false;
            recordingStatus.textContent = "Recording in progress...";
            recordingStatus.style.color = "#E0245E";
            
            // Start timer
            startRecordingTimer();
            
        } catch (error) {
            console.error('Error accessing microphone:', error);
            alert('Could not access microphone. Please check permissions or use file upload instead.');
        }
    });

    // Stop recording function
    stopRecordingBtn.addEventListener('click', () => {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            stopRecordingTimer();
            
            // Update UI
            startRecordingBtn.disabled = false;
            stopRecordingBtn.disabled = true;
            recordingStatus.textContent = "Recording stopped";
            recordingStatus.style.color = "";
        }
    });

    // File upload handling
    audioFileInput.addEventListener('change', (event) => {
        if (event.target.files && event.target.files[0]) {
            audioFile = event.target.files[0];
            
            // Check if file is audio
            if (!audioFile.type.startsWith('audio/')) {
                alert('Please select an audio file');
                return;
            }
            
            // Update UI
            fileName.textContent = audioFile.name;
            
            // Create a URL for the audio player
            const audioUrl = URL.createObjectURL(audioFile);
            audioPlayer.src = audioUrl;
            
            // Show audio preview
            audioPreview.classList.remove('hidden');
        }
    });

    // Submit audio to create tweets
    submitAudioBtn.addEventListener('click', async () => {
        if (!audioFile) {
            alert('Please record audio or upload a voice memo first');
            return;
        }
        
        try {
            // Show processing status
            statusContainer.classList.remove('hidden');
            processingStatus.textContent = "Preparing to upload...";
            updateProgressBar(10);
            
            // Convert audio to base64 for GitHub API
            const base64Audio = await fileToBase64(audioFile);
            processingStatus.textContent = "Uploading audio...";
            updateProgressBar(30);
            
            // Upload via GitHub API (requires authentication)
            await uploadAudioToGitHub(base64Audio, audioFile.name);
            
            // Update status
            processingStatus.textContent = "Audio uploaded successfully. Tweet generation in progress...";
            updateProgressBar(70);
            
            // Simulated delay (in real implementation, would poll for status)
            setTimeout(() => {
                processingStatus.textContent = "Tweets have been generated and scheduled for posting!";
                updateProgressBar(100);
                
                // Could redirect to a status page or show tweet previews here
            }, 3000);
            
        } catch (error) {
            console.error('Error submitting audio:', error);
            processingStatus.textContent = "Error: " + error.message;
            updateProgressBar(0);
        }
    });

    // Helper functions
    function startRecordingTimer() {
        recordingTimer = setInterval(() => {
            recordingSeconds++;
            updateRecordingTime();
        }, 1000);
    }

    function stopRecordingTimer() {
        clearInterval(recordingTimer);
    }

    function updateRecordingTime() {
        const minutes = Math.floor(recordingSeconds / 60).toString().padStart(2, '0');
        const seconds = (recordingSeconds % 60).toString().padStart(2, '0');
        recordingTime.textContent = `${minutes}:${seconds}`;
    }

    function updateProgressBar(percentage) {
        progressBar.style.width = `${percentage}%`;
    }

    function fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => {
                // Extract the base64 data from the result
                const base64Data = reader.result.split(',')[1];
                resolve(base64Data);
            };
            reader.onerror = error => reject(error);
        });
    }

    // In a real implementation, this would use GitHub API with proper authentication
    // This is a simplified version to demonstrate the concept
    async function uploadAudioToGitHub(base64Content, filename) {
        // In the actual implementation, this would use GitHub's API to create a commit
        // For now, we'll simulate success after a delay
        return new Promise(resolve => {
            setTimeout(() => {
                console.log(`Simulated upload of ${filename} to GitHub`);
                resolve({ success: true });
            }, 1500);
        });
        
        /* 
        // Example of actual implementation using GitHub API (commented out)
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const path = `audio/${timestamp}-${filename}`;
        
        const response = await fetch('https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO/contents/' + path, {
            method: 'PUT',
            headers: {
                'Authorization': `token ${YOUR_GITHUB_TOKEN}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: `Add audio file: ${filename}`,
                content: base64Content,
                branch: 'main'
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to upload to GitHub');
        }
        
        return response.json();
        */
    }
});