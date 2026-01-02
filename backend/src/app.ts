import { 
  RTVIClient, 
  RTVIEvent, 
  RTVIMessage, 
  Participant, 
  BotLLMTextData, 
  Transport 
} from "@pipecat-ai/client-js";
import { DailyTransport } from "@pipecat-ai/daily-transport";

const ngrokUrl = import.meta.env.VITE_NGROK_URL;


let joinDiv: HTMLElement;
let audioDiv: HTMLDivElement;
let chatTextDiv: HTMLDivElement;
let currentUserSpeechDiv: HTMLDivElement;
let currentBotSpeechDiv: HTMLDivElement;
let currentSpeaker = ''; // 'user' or 'bot'

export type TranscriptData = {
  text: string;
  final: boolean;
  timestamp: string;
  user_id: string;
};

document.addEventListener('DOMContentLoaded', () => {
  joinDiv = document.getElementById('join-div');
  document.getElementById('start-webrtc-transport-session').addEventListener('click', () => {
    startBot('daily');
  });
});

function getUserFromURL(): string | null {
  const path = window.location.pathname;
  return path.slice(1);
}


async function startBot(profileChoice: string) {
  let transport: Transport;

  joinDiv.textContent = 'Joining...';

  console.log('-- starting Gemini WebRTC connection --');
  transport = new DailyTransport();

  const rtviClient = new RTVIClient({
    transport,
    params: {
      baseUrl: `https://${ngrokUrl}/`,
    },
    enableMic: true,
    enableCam: false,
    timeout: 30 * 1000,
  });

  setupEventHandlers(rtviClient);

  try {
    await rtviClient.initDevices();
    await rtviClient.connect();
  } catch (e) {
    console.log('Error connecting', e);
  }
}


export async function setupEventHandlers(rtviClient: RTVIClient) {
  audioDiv = document.getElementById('audio') as HTMLDivElement;
  chatTextDiv = document.getElementById('chat-text') as HTMLDivElement;

  rtviClient.on(RTVIEvent.TransportStateChanged, (state: string) => {
    console.log(`-- transport state change: ${state} --`);
    joinDiv.textContent = `Transport state: ${state}`;
  });

  rtviClient.on(RTVIEvent.Connected, () => {
    console.log("-- user connected --");
  });

  rtviClient.on(RTVIEvent.Disconnected, () => {
    console.log("-- user disconnected --");
  });

  rtviClient.on(RTVIEvent.BotConnected, () => {
    console.log("-- bot connected --");
  });

  rtviClient.on(RTVIEvent.BotDisconnected, () => {
    console.log("--bot disconnected --");
  });

  rtviClient.on(RTVIEvent.BotReady, () => {
    console.log("-- bot ready to chat! --");
  });

  rtviClient.on(RTVIEvent.TrackStarted, (track: MediaStreamTrack, participant: Participant) => {
    console.log(" --> track started", participant, track);
    if (participant.local) {
      return;
    }
    let audio = document.createElement("audio");
    audio.srcObject = new MediaStream([track]);
    audio.autoplay = true;
    audioDiv.appendChild(audio);
  });

  rtviClient.on(RTVIEvent.UserStartedSpeaking, startUserSpeechBubble);
  rtviClient.on(RTVIEvent.UserStoppedSpeaking, finishUserSpeechBubble);
  rtviClient.on(RTVIEvent.BotStartedSpeaking, startBotSpeechBubble);
  rtviClient.on(RTVIEvent.BotStoppedSpeaking, finishBotSpeechBubble);

  rtviClient.on(RTVIEvent.UserTranscript, (transcript: TranscriptData) => {
    if (transcript.final) {
      handleUserFinalTranscription(transcript.text);
    } else {
      handleUserInterimTranscription(transcript.text);
    }
  });

  rtviClient.on(RTVIEvent.BotTranscript, handleBotLLMText);
  rtviClient.on(RTVIEvent.Error, (message: RTVIMessage) => {
    console.log("[EVENT] RTVI Error!", message);
  });

  rtviClient.on(RTVIEvent.MessageError, (message: RTVIMessage) => {
    console.log("[EVENT] RTVI ErrorMessage error!", message);
  });

  rtviClient.on(RTVIEvent.Metrics, (data) => {
    if (!data.ttfb) {
      return;
    }
    data.ttfb.map((metric) => {
      console.log(`[METRICS] ${metric.processor} ttfb: ${metric.value}`);
    });
  });
}

// Handle user speech bubble appearance
async function startUserSpeechBubble() {
  console.log('-- user started speaking --');
  if (currentSpeaker === 'user') {
    if (currentUserSpeechDiv) {
      return;
    }
  }
  currentSpeaker = 'user';
  currentUserSpeechDiv = document.createElement('div');
  currentUserSpeechDiv.className = 'user-message';
  let span = document.createElement('span');
  currentUserSpeechDiv.appendChild(span);
  chatTextDiv.appendChild(currentUserSpeechDiv);
}

// Handle user stopping speech
async function finishUserSpeechBubble() {
  console.log('-- user stopped speaking --');
}

// Handle bot speech bubble appearance
async function startBotSpeechBubble() {
  currentSpeaker = 'bot';
  currentBotSpeechDiv = document.createElement('div');
  currentBotSpeechDiv.className = 'assistant-message';
  chatTextDiv.appendChild(currentBotSpeechDiv);
}

// Handle bot stopping speech
async function finishBotSpeechBubble() {
  console.log('-- bot stopped speaking --');
}

// Handle interim transcription from the user
async function handleUserInterimTranscription(text: string) {
  console.log('interim transcription:', text);
  if (currentSpeaker !== 'user') {
    return;
  }
  let span = currentUserSpeechDiv.querySelector('span:last-of-type');
  span.classList.add('interim');
  span.textContent = text + " ";
  scroll();
}

// Handle final transcription from the user
async function handleUserFinalTranscription(text: string) {
  console.log('final transcription:', text);
  let span = currentUserSpeechDiv.querySelector('span:last-of-type');
  span.classList.remove('interim');
  span.textContent = text + " ";
  let newSpan = document.createElement('span');
  currentUserSpeechDiv.appendChild(newSpan);
  scroll();
}

// Handle bot LLM text
async function handleBotLLMText(data: BotLLMTextData) {
  console.log('bot llm text:', data.text);
  if (!currentBotSpeechDiv) {
    return;
  }
  currentBotSpeechDiv.textContent += data.text;
  scroll();
}

// Scroll to the bottom of the chat
function scroll() {
  window.scrollTo({
    top: document.body.scrollHeight,
    behavior: 'smooth'
  });
}
