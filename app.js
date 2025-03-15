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
            
            // Create form data for upload
            const formData = new FormData();
            formData.append('audio', audioFile);
            
            processingStatus.textContent = "Uploading audio...";
            updateProgressBar(30);
            
            // Upload to Vercel API endpoint
            const response = await fetch('/api/process_audio', {
                method: 'POST',
                body: formData,
            });
            
            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}: ${await response.text()}`);
            }
            
            const data = await response.json();
            
            // Update status
            processingStatus.textContent = "Audio processed successfully. Tweets are being posted...";
            updateProgressBar(70);
            
            // Poll for status
            const statusCheckInterval = setInterval(async () => {
                const statusResponse = await fetch(`/api/status?id=${data.jobId}`);
                const statusData = await statusResponse.json();
                
                if (statusData.status === 'completed') {
                    clearInterval(statusCheckInterval);
                    processingStatus.textContent = `${statusData.tweets.length} tweets have been posted!`;
                    updateProgressBar(100);
                    
                    // Display the tweets
                    const tweetsList = document.createElement('div');
                    tweetsList.className = 'tweets-list';
                    
                    statusData.tweets.forEach(tweet => {
                        const tweetElement = document.createElement('div');
                        tweetElement.className = 'tweet';
                        tweetElement.textContent = tweet.text;
                        tweetsList.appendChild(tweetElement);
                    });
                    
                    statusContainer.appendChild(tweetsList);
                } else if (statusData.status === 'failed') {
                    clearInterval(statusCheckInterval);
                    processingStatus.textContent = `Error: ${statusData.error}`;
                    updateProgressBar(0);
                }
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
});