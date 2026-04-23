import React, { useEffect, useRef } from 'react';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';

interface WatchPageProps {
  params: { file_id: string };
  searchParams: { anime: string; season: string; ep: string };
}

const WatchPage: React.FC<WatchPageProps> = ({ params, searchParams }) => {
  const videoRef = useRef<HTMLDivElement>(null);
  const playerRef = useRef<any>(null);
  const { file_id } = params;
  const { anime, season, ep } = searchParams;

  const streamUrl = `${process.env.NEXT_PUBLIC_BOT_URL}/stream/${file_id}`;

  useEffect(() => {
    if (!playerRef.current && videoRef.current) {
      const videoElement = document.createElement('video-js');
      videoElement.classList.add('vjs-big-play-centered');
      videoRef.current.appendChild(videoElement);

      const player = (playerRef.current = videojs(videoElement, {
        autoplay: false,
        controls: true,
        responsive: true,
        fluid: true,
        sources: [{ src: streamUrl, type: 'video/mp4' }],
      }));
    }
  }, [videoRef, streamUrl]);

  useEffect(() => {
    const player = playerRef.current;
    return () => {
      if (player && !player.isDisposed()) {
        player.dispose();
        playerRef.current = null;
      }
    };
  }, [playerRef]);

  return (
    <div className="min-h-screen bg-[#0a0a0b] text-white font-sans p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-pink-500 to-blue-500 bg-clip-text text-transparent drop-shadow-[0_0_10px_rgba(255,0,255,0.5)]">
            OTAKULUX
          </h1>
          <div className="hidden md:block">
            <input
              type="text"
              placeholder="Search Anime..."
              className="bg-[#1a1a1c] border border-pink-500/30 rounded-full px-6 py-2 focus:outline-none focus:border-pink-500 transition-all shadow-[0_0_15px_rgba(255,0,255,0.1)]"
            />
          </div>
        </header>

        {/* Player Section */}
        <main className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="rounded-2xl overflow-hidden border-2 border-pink-500/20 shadow-[0_0_30px_rgba(255,0,255,0.1)] backdrop-blur-md">
              <div ref={videoRef} />
            </div>

            {/* External Players */}
            <div className="mt-4 flex flex-wrap gap-3">
              <a
                href={`vlc://${streamUrl}`}
                className="bg-orange-600/20 hover:bg-orange-600/40 text-orange-400 border border-orange-600/30 px-4 py-2 rounded-lg text-sm font-medium transition-all"
              >
                Open in VLC
              </a>
              <a
                href={`intent:${streamUrl}#Intent;package=com.mxtech.videoplayer.ad;end`}
                className="bg-blue-600/20 hover:bg-blue-600/40 text-blue-400 border border-blue-600/30 px-4 py-2 rounded-lg text-sm font-medium transition-all"
              >
                Open in MX Player
              </a>
              <a
                href={`playit://${streamUrl}`}
                className="bg-purple-600/20 hover:bg-purple-600/40 text-purple-400 border border-purple-600/30 px-4 py-2 rounded-lg text-sm font-medium transition-all"
              >
                Open in PlayIt
              </a>
            </div>

            <div className="mt-6">
              <h2 className="text-2xl font-semibold text-pink-400 mb-2">{anime || 'Loading Anime...'}</h2>
              <div className="flex gap-4 text-sm text-gray-400">
                <span className="bg-blue-500/10 text-blue-400 px-3 py-1 rounded-full border border-blue-500/20">Season {season || '1'}</span>
                <span className="bg-pink-500/10 text-pink-400 px-3 py-1 rounded-full border border-pink-500/20">Episode {ep || '1'}</span>
              </div>
              <p className="mt-4 text-gray-300 leading-relaxed">
                Experience the best quality streaming only on OTAKULUX. Join our Telegram for more updates!
              </p>
            </div>
          </div>

          {/* Sidebar / Controls */}
          <div className="bg-[#121214] rounded-2xl p-6 border border-white/5 backdrop-blur-md">
            <h3 className="text-xl font-bold text-blue-400 mb-4 flex items-center gap-2">
              <span className="w-2 h-8 bg-blue-500 rounded-full"></span>
              Episode Selector
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-xs uppercase text-gray-500 mb-2 font-bold tracking-widest">Select Season</label>
                <select className="w-full bg-[#1a1a1c] border border-white/10 rounded-xl px-4 py-3 focus:border-pink-500 outline-none transition-all">
                  <option>Season 1</option>
                  <option>Season 2</option>
                </select>
              </div>

              <div>
                <label className="block text-xs uppercase text-gray-500 mb-2 font-bold tracking-widest">Select Episode</label>
                <div className="grid grid-cols-4 gap-2">
                  {[...Array(12)].map((_, i) => (
                    <button
                      key={i}
                      className={`py-2 rounded-lg border transition-all ${i === Number(ep) - 1 ? 'bg-pink-600 border-pink-500 shadow-[0_0_15px_rgba(255,0,255,0.4)]' : 'bg-[#1a1a1c] border-white/5 hover:border-pink-500/50'}`}
                    >
                      {i + 1}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-12">
              <h3 className="text-xl font-bold text-pink-400 mb-4 flex items-center gap-2">
                <span className="w-2 h-8 bg-pink-500 rounded-full"></span>
                Top Genres
              </h3>
              <div className="flex flex-wrap gap-2">
                {['Action', 'Sci-Fi', 'Fantasy', 'Shonen'].map(genre => (
                  <span key={genre} className="px-3 py-1 bg-white/5 rounded-full text-xs hover:bg-pink-500/20 cursor-pointer transition-colors border border-white/5">
                    {genre}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default WatchPage;
