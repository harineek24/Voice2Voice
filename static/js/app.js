document.addEventListener('DOMContentLoaded', () => {
    const recordButton = document.getElementById('recordButton');
    const statusElement = document.getElementById('status');
    const messagesContainer = document.getElementById('messagesContainer');
    
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    
    // Set up audio recording
    async function setupRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.addEventListener('dataavailable', event => {
                audioChunks.push(event.data);
            });
            
            mediaRecorder.addEventListener('stop', async () => {
                statusElement.textContent = 'Processing...';
                
                // Create audio blob from recorded chunks
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                
                // Add user message to UI
                addMessage('You', 'Recording sent', 'user');
                
                // Send to backend
                await sendAudioToBackend(audioBlob);
                
                // Reset chunks for next recording
                audioChunks = [];
            });
            
            return true;
        } catch (error) {
            console.error('Error accessing microphone:', error);
            statusElement.textContent = 'Error: Microphone access denied';
            return false;
        }
    }
    
    // Toggle recording state
    async function toggleRecording() {
        if (!mediaRecorder && !isRecording) {
            const setupSuccess = await setupRecording();
            if (!setupSuccess) return;
        }
        
        if (isRecording) {
            // Stop recording
            mediaRecorder.stop();
            recordButton.textContent = 'Start Recording';
            recordButton.classList.remove('recording');
            statusElement.textContent = 'Processing...';
        } else {
            // Start recording
            audioChunks = [];
            mediaRecorder.start();
            recordButton.textContent = 'Stop Recording';
            recordButton.classList.add('recording');
            statusElement.textContent = 'Recording...';
        }
        
        isRecording = !isRecording;
    }
    
    // Get ephemeral key from server
    async function getEphemeralKey() {
        try {
            const response = await fetch('/api/key');
            if (!response.ok) {
                throw new Error('Failed to get ephemeral key');
            }
            const data = await response.json();
            return data.key;
        } catch (error) {
            console.error('Error getting ephemeral key:', error);
            return null;
        }
    }
    
    // Send audio to backend
    async function sendAudioToBackend(audioBlob) {
        try {
            // Get ephemeral key first
            const key = await getEphemeralKey();
            if (!key) {
                statusElement.textContent = 'Error: Could not get API key';
                return;
            }
            
            const formData = new FormData();
            formData.append('audio', audioBlob);
            
            const response = await fetch('/api/process-voice', {
                method: 'POST',
                headers: {
                    'X-API-Key': key
                },
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}`);
            }
            
            const responseData = await response.json();
            
            // Play response audio
            const audio = new Audio(responseData.audio_url);
            audio.play();
            
            // Add assistant message to UI
            addMessage('Assistant', responseData.text, 'assistant');
            
            statusElement.textContent = 'Ready';
        } catch (error) {
            console.error('Error sending audio to backend:', error);
            statusElement.textContent = 'Error processing request';
        }
    }
    
    // Add message to conversation UI
    function addMessage(sender, text, type) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}-message`;
        
        const headerElement = document.createElement('div');
        headerElement.className = `message-header ${type}-header`;
        headerElement.textContent = sender;
        
        const textElement = document.createElement('div');
        textElement.className = 'message-text';
        textElement.textContent = text;
        
        messageElement.appendChild(headerElement);
        messageElement.appendChild(textElement);
        messagesContainer.appendChild(messageElement);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Set up event listeners
    recordButton.addEventListener('click', toggleRecording);
});