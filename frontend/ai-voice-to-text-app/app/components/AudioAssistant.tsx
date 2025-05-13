import React, { useRef, useState } from "react";

type AudioSource = "microphone" | "system";

export default function AudioAssistant() {
    const [recording, setRecording] = useState(false);
    const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
    const [status, setStatus] = useState("");
    const [result, setResult] = useState({ transcript: "", answer: "" });
    const [audioSource, setAudioSource] = useState<AudioSource>("microphone");
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);

    // Hotkey handler
    React.useEffect(() => {
        function handleKeydown(e: KeyboardEvent) {
            if (e.key.toLowerCase() === "r" && !e.repeat) {
                if (!recording) startRecording();
                else stopRecording();
            }
            // CapsLock + A to analyze (you may fine-tune this UI pattern)
            if (
                e.key.toLowerCase() === "a"
            ) {
                analyzeAudio();
            }
        }
        window.addEventListener("keydown", handleKeydown);
        return () => window.removeEventListener("keydown", handleKeydown);
        // Only refetches if recording/audioBlob change
    }, [recording, audioBlob, audioSource]);

    async function startRecording() {
        setStatus(`Recording (${audioSource})...`);
        setRecording(true);
        audioChunksRef.current = [];

        if (audioSource === "microphone") {
            // Mic input
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                startMediaRecorder(stream);
            } catch (e) {
                setStatus("Microphone access denied or unavailable.");
                setRecording(false);
            }
        } else {
            // "System audio" mode explanation
            // Web browsers cannot natively record system output for security reasons,
            // except when the OS or browser offers "stereo mix"/loopback---which is rare.
            // We'll inform the user and attempt to capture if possible.
            // (Most browsers reject `{audio: {mediaSource: "system"}}`)
            setStatus(
                "Recording of system/desktop audio is restricted by browsers for security reasons. " +
                "You can try using 'Stereo Mix' input (if available) or use the Microphone option."
            );
            setRecording(false);
        }
    }

    function startMediaRecorder(stream: MediaStream) {
        const mediaRecorder = new window.MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;

        mediaRecorder.ondataavailable = (e) => {
            audioChunksRef.current.push(e.data);
        };
        mediaRecorder.onstop = () => {
            const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
            setAudioBlob(blob);
            setStatus("Recorded. Ready for analysis.");
            // Stop all tracks
            stream.getTracks().forEach((t) => t.stop());
        };

        mediaRecorder.start();
    }

    function stopRecording() {
        setStatus("Stopping...");
        setRecording(false);
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
            // No need to stop tracks here; done on onstop
        }
    }

    async function analyzeAudio() {
        if (!audioBlob) {
            setStatus("No audio recorded!");
            return;
        }
        setStatus("Transcribing audio...");
        const formData = new FormData();
        formData.append("audio", audioBlob, "input.webm");
        const resTranscribe = await fetch("http://localhost:8000/transcribe/", {
            method: "POST",
            body: formData,
        });
        const transcribeData = await resTranscribe.json();
        setStatus("Generating answer...");

        // --- Fix here: use FormData not JSON, and field must be "transcript"
        const answerFormData = new FormData();
        answerFormData.append("transcript", transcribeData.transcript); // <-- use .transcript
        // Optionally control use_llm:
        // answerFormData.append("use_llm", "true");

        const resAnswer = await fetch("http://localhost:8000/generate-response/", {
            method: "POST",
            body: answerFormData,
        });
        const answerData = await resAnswer.json();

        setResult({
            transcript: transcribeData.transcript,
            answer: answerData.answer || answerData.result || "",
        });
        setStatus("Done.");
    }

    function speak(text: string) {
        if ("speechSynthesis" in window) {
            window.speechSynthesis.cancel();
            const utterance = new window.SpeechSynthesisUtterance(text);
            window.speechSynthesis.speak(utterance);
        }
    }

    return (
        <div style={{ maxWidth: 600, margin: "auto", fontFamily: "sans-serif" }}>
            <div style={{ marginBottom: 10 }}>
                <b>Audio Source:&nbsp;</b>
                <label>
                    <input
                        type="radio"
                        value="microphone"
                        checked={audioSource === "microphone"}
                        onChange={() => setAudioSource("microphone")}
                        disabled={recording}
                    />
                    Microphone
                </label>
                &nbsp;
                <label>
                    <input
                        type="radio"
                        value="system"
                        checked={audioSource === "system"}
                        onChange={() => setAudioSource("system")}
                        disabled={recording}
                    />
                    System Audio (Teams/Meet)
                </label>
                <span style={{ color: "#b44", fontSize: 12, marginLeft: 12 }}>
                    {audioSource === "system"
                        ? "System audio capture is limited in browsers. See help below."
                        : ""}
                </span>
            </div>
            <div>
                <b>Press <kbd>R</kbd> to start/stop recording</b><br />
                <b>Press <kbd>A</kbd> (Caps Lock + A) to analyze</b>
            </div>
            <div>Status: {status}</div>
            <div>
                <b>Transcript:</b>
                <pre>{result.transcript}</pre>
            </div>
            <div>
                <b>AI Answer:</b>
                <pre>{result.answer}</pre>
                {result.answer && (
                    <button onClick={() => speak(result.answer)}>🔊 Speak</button>
                )}
            </div>
            <div style={{ marginTop: 24, color: "#888", fontSize: 13 }}>
                <b>Note:</b>
                System audio (what you hear from headphones/speakers) recording requires OS support for "stereo mix" or loopback devices.
                Browsers, for privacy and security, block direct system audio capture.<br/>
                If you need to record system audio, use the Microphone option or record from the system-level audio device if available.
            </div>
        </div>
    );
}