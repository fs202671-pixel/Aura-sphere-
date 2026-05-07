import React, { useEffect, useState } from 'react';

interface WindowWithSpeech extends Window {
  SpeechRecognition?: typeof SpeechRecognition | typeof webkitSpeechRecognition;
  webkitSpeechRecognition?: typeof SpeechRecognition;
}

declare global {
  interface Window {
    SpeechRecognition?: typeof SpeechRecognition;
    webkitSpeechRecognition?: typeof SpeechRecognition;
  }
}

export function VoiceMode() {
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [support, setSupport] = useState(true);

  useEffect(() => {
    const SpeechRecognition = (window as WindowWithSpeech).SpeechRecognition || (window as WindowWithSpeech).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setSupport(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'pt-BR';
    recognition.interimResults = true;
    recognition.continuous = true;

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const last = event.results[event.results.length - 1];
      setTranscript(last[0].transcript);
    };

    recognition.onstart = () => setListening(true);
    recognition.onend = () => setListening(false);

    if (listening) {
      recognition.start();
    } else {
      recognition.stop();
    }

    return () => {
      recognition.stop();
    };
  }, [listening]);

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-3xl font-bold text-white">Voice Mode</h2>
      <p className="text-slate-300 max-w-3xl">
        Use a voz para controlar a interface e ditar comandos. O sistema tenta capturar sua fala e exibir o texto em tempo real.
      </p>

      {!support ? (
        <div className="rounded-3xl bg-slate-700/70 border border-slate-600 p-6">
          <p className="text-slate-200">Seu navegador não suporta reconhecimento por voz nativo.</p>
          <p className="text-slate-400">Use Chrome ou Edge para uma melhor experiência de voz.</p>
        </div>
      ) : (
        <div className="space-y-4">
          <button
            onClick={() => setListening((value) => !value)}
            className={`rounded-full px-8 py-4 text-lg font-semibold transition ${
              listening ? 'bg-emerald-500 text-black' : 'bg-slate-700 text-white hover:bg-slate-600'
            }`}
          >
            {listening ? 'Parar escuta' : 'Iniciar escuta'}
          </button>

          <div className="rounded-3xl bg-slate-800/70 border border-slate-600 p-6 min-h-[180px]">
            <h3 className="text-lg font-semibold text-white mb-3">Transcrição</h3>
            <p className="text-slate-200 whitespace-pre-line min-h-[100px]">{transcript || 'Nenhuma fala detectada ainda.'}</p>
          </div>
        </div>
      )}
    </div>
  );
}
