import { useState, useEffect } from 'react';
import Head from 'next/head';
import VoiceRecognition from '../components/VoiceRecognition';
import UserIdentification from '../components/UserIdentification';
import ResponseGenerator from '../components/ResponseGenerator';

export default function Home() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [isOwner, setIsOwner] = useState(true);
  const [hasOwnerProfile, setHasOwnerProfile] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
  const [status, setStatus] = useState('Ready');

  // Check if owner profile exists
  useEffect(() => {
    const ownerProfile = localStorage.getItem('ownerProfile');
    setHasOwnerProfile(!!ownerProfile);
  }, []);

  // Handle speech recognition result
  const handleSpeechResult = (text, audioData) => {
    setTranscript(text);
    
    // Check for exit commands
    if (text.toLowerCase().includes('exit') || 
        text.toLowerCase().includes('quit') || 
        text.toLowerCase().includes('goodbye')) {
      setResponse('Exiting Voice Recognition AI. Goodbye!');
      setIsListening(false);
      return;
    }

    // If registering owner, save profile
    if (isRegistering) {
      handleRegisterOwner(audioData);
      return;
    }

    // Identify user
    const userIsOwner = identifyUser(audioData);
    setIsOwner(userIsOwner);

    // Generate response
    const responseText = generateResponse(text);
    setResponse(responseText);
  };

  // Register owner profile
  const handleRegisterOwner = (audioData) => {
    // Extract features and save to localStorage
    const features = extractFeatures(audioData);
    localStorage.setItem('ownerProfile', JSON.stringify(features));
    
    setHasOwnerProfile(true);
    setIsRegistering(false);
    setResponse('Owner profile registered successfully!');
  };

  // Start owner registration process
  const startRegistration = () => {
    setIsRegistering(true);
    setStatus('Please say "This is the owner speaking" when prompted');
    setIsListening(true);
  };

  // Extract audio features (simplified version)
  const extractFeatures = (audioData) => {
    // In a real implementation, this would use a library like Meyda
    // to extract MFCC features from the audio data
    return { timestamp: Date.now(), sample: audioData.slice(0, 1000) };
  };

  // Identify if user is owner
  const identifyUser = (audioData) => {
    if (!hasOwnerProfile) return false;
    
    try {
      const ownerFeatures = JSON.parse(localStorage.getItem('ownerProfile'));
      const currentFeatures = extractFeatures(audioData);
      
      // In a real implementation, this would compare MFCC features
      // using cosine similarity or another method
      // For demo purposes, we'll just return true 50% of the time
      return Math.random() > 0.5;
    } catch (error) {
      console.error('Error identifying user:', error);
      return false;
    }
  };

  // Generate response based on user query
  const generateResponse = (query) => {
    const queryLower = query.toLowerCase();
    
    // Simple response generation based on keywords
    if (queryLower.includes('hello') || queryLower.includes('hi')) {
      return 'Hello! How can I help you today?';
    } else if (queryLower.includes('weather')) {
      return 'I\'m sorry, I don\'t have access to weather information at the moment.';
    } else if (queryLower.includes('time')) {
      return 'I don\'t have access to the current time. You might want to check your device\'s clock.';
    } else if (queryLower.includes('thank')) {
      return 'You\'re welcome!';
    } else {
      return 'I\'m not sure how to respond to that. Could you rephrase?';
    }
  };

  // Toggle listening state
  const toggleListening = () => {
    setIsListening(!isListening);
    if (!isListening) {
      setStatus('Listening...');
    } else {
      setStatus('Ready');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <Head>
        <title>Voice Recognition AI</title>
        <meta name="description" content="Voice Recognition AI application" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-light-blue-500 shadow-lg transform -skew-y-6 sm:skew-y-0 sm:-rotate-6 sm:rounded-3xl"></div>
        <div className="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          <div className="max-w-md mx-auto">
            <div className="divide-y divide-gray-200">
              <div className="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                <h1 className="text-3xl font-extrabold text-center">Voice Recognition AI</h1>
                
                {!hasOwnerProfile && !isRegistering && (
                  <div className="mt-8 text-center">
                    <p className="mb-4">No owner profile found. Let's set up your voice profile.</p>
                    <button 
                      onClick={startRegistration}
                      className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                      Register Owner Voice
                    </button>
                  </div>
                )}

                {(hasOwnerProfile || isRegistering) && (
                  <>
                    <div className="mt-8">
                      <p className="text-center font-semibold">{status}</p>
                      
                      <div className="mt-4 flex justify-center">
                        <button 
                          onClick={toggleListening}
                          className={`px-4 py-2 rounded ${isListening ? 'bg-red-500 hover:bg-red-600' : 'bg-green-500 hover:bg-green-600'} text-white`}
                        >
                          {isListening ? 'Stop Listening' : 'Start Listening'}
                        </button>
                      </div>
                    </div>

                    {transcript && (
                      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                        <h2 className="text-lg font-semibold">You said:</h2>
                        <p className="mt-2">{transcript}</p>
                      </div>
                    )}

                    {response && (
                      <div className={`mt-6 p-4 rounded-lg ${isOwner ? 'bg-blue-50' : 'bg-yellow-50'}`}>
                        {!isOwner && <p className="text-yellow-600 font-bold">[Different User Detected]</p>}
                        <h2 className="text-lg font-semibold">Response:</h2>
                        <p className={`mt-2 ${!isOwner ? 'text-yellow-600 font-semibold' : ''}`}>{response}</p>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Voice Recognition Component (hidden) */}
      {isListening && (
        <VoiceRecognition 
          onResult={handleSpeechResult}
          onError={(error) => setStatus(`Error: ${error}`)}
        />
      )}
    </div>
  );
}