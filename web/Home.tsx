import React from 'react';

const HomePage = () => {
  const trendingAnime = [
    { id: 1, title: 'Solo Leveling', image: 'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx151807-6ion9ex4N9Yv.png', rating: '9.2' },
    { id: 2, title: 'Jujutsu Kaisen', image: 'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx113415-bbBWjdfjBAEJ.png', rating: '8.8' },
    { id: 3, title: 'One Piece', image: 'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21-YCDoj1EkAxFn.jpg', rating: '9.5' },
    { id: 4, title: 'Demon Slayer', image: 'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx101922-W3SeF3p9Z9Yj.jpg', rating: '8.7' },
  ];

  const latestAnime = [
    { id: 5, title: 'Naruto Shippuden', image: 'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx1735-v0i76vH76Zp3.jpg' },
    { id: 6, title: 'Bleach TYBW', image: 'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx142769-9pP0I6X6P6X6.png' },
    { id: 7, title: 'Zoro', image: 'https://telegra.ph/file/ec17880d61180d3312d6a.jpg' },
    { id: 8, title: 'Black Clover', image: 'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx97940-9pP0I6X6P6X6.png' },
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0b] text-white font-sans">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <header className="flex justify-between items-center mb-12">
          <h1 className="text-4xl font-extrabold bg-gradient-to-r from-pink-500 to-blue-500 bg-clip-text text-transparent drop-shadow-[0_0_15px_rgba(255,0,255,0.6)]">
            OTAKULUX
          </h1>
          <nav className="hidden md:flex gap-8 text-sm font-bold uppercase tracking-widest text-gray-400">
            <a href="#" className="hover:text-pink-500 transition-colors">Home</a>
            <a href="#" className="hover:text-pink-500 transition-colors">Movies</a>
            <a href="#" className="hover:text-pink-500 transition-colors">Series</a>
            <a href="#" className="hover:text-pink-500 transition-colors">Ongoing</a>
          </nav>
        </header>

        {/* Hero Section */}
        <div className="relative h-[400px] rounded-3xl overflow-hidden mb-16 border border-white/10 group">
          <img
            src="https://telegra.ph/file/e292b12890b8b4b9dcbd1.jpg"
            alt="Hero"
            className="w-full h-full object-cover opacity-60 group-hover:scale-105 transition-transform duration-700"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0b] via-transparent to-transparent"></div>
          <div className="absolute bottom-10 left-10 max-w-2xl">
            <span className="bg-pink-600 text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-tighter mb-4 inline-block shadow-[0_0_10px_rgba(255,0,255,0.5)]">Trending Now</span>
            <h2 className="text-5xl font-black mb-4 drop-shadow-2xl">Solo Leveling</h2>
            <p className="text-gray-300 text-lg mb-8 line-clamp-2">The weakest hunter of all mankind, Sung Jin-woo, finds himself in a double dungeon and discovers a secret that will change his life forever.</p>
            <button className="bg-white text-black px-8 py-3 rounded-xl font-bold hover:bg-pink-500 hover:text-white transition-all transform hover:-translate-y-1">Watch Now</button>
          </div>
        </div>

        {/* Trending Section */}
        <section className="mb-16">
          <div className="flex items-center gap-4 mb-8">
            <span className="w-2 h-10 bg-pink-500 rounded-full shadow-[0_0_15px_rgba(255,0,255,0.8)]"></span>
            <h3 className="text-2xl font-black uppercase tracking-tight">Trending Anime</h3>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
            {trendingAnime.map(anime => (
              <div key={anime.id} className="relative group cursor-pointer">
                <div className="aspect-[2/3] rounded-2xl overflow-hidden border border-white/5 group-hover:border-pink-500/50 transition-all shadow-2xl">
                  <img src={anime.image} alt={anime.title} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-sm">
                    <button className="bg-pink-600 p-4 rounded-full shadow-[0_0_20px_rgba(255,0,255,0.6)]">
                      <svg className="w-6 h-6 fill-white" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                    </button>
                  </div>
                </div>
                <div className="absolute top-3 right-3 bg-black/60 backdrop-blur-md px-2 py-1 rounded-lg border border-white/10 text-[10px] font-bold text-yellow-400">
                  ⭐ {anime.rating}
                </div>
                <h4 className="mt-4 font-bold text-sm group-hover:text-pink-500 transition-colors line-clamp-1">{anime.title}</h4>
              </div>
            ))}
          </div>
        </section>

        {/* Latest Section */}
        <section>
          <div className="flex items-center gap-4 mb-8">
            <span className="w-2 h-10 bg-blue-500 rounded-full shadow-[0_0_15px_rgba(59,130,246,0.8)]"></span>
            <h3 className="text-2xl font-black uppercase tracking-tight">Latest Episodes</h3>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
            {latestAnime.map(anime => (
              <div key={anime.id} className="relative group cursor-pointer">
                <div className="aspect-[2/3] rounded-2xl overflow-hidden border border-white/5 group-hover:border-blue-500/50 transition-all">
                  <img src={anime.image} alt={anime.title} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
                  <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/90 to-transparent">
                    <span className="text-[10px] font-black text-blue-400 uppercase tracking-widest">Episode 12</span>
                  </div>
                </div>
                <h4 className="mt-4 font-bold text-sm group-hover:text-blue-400 transition-colors line-clamp-1">{anime.title}</h4>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* Footer */}
      <footer className="mt-20 border-t border-white/5 py-12 bg-[#080809]">
        <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center gap-8">
          <p className="text-gray-500 text-sm font-medium">© 2025 <span className="text-pink-500">OTAKULUX</span>. Built for the community.</p>
          <div className="flex gap-6">
             <a href="https://t.me/OTAKULUX" className="text-gray-400 hover:text-blue-400 text-sm font-bold">Telegram</a>
             <a href="#" className="text-gray-400 hover:text-pink-400 text-sm font-bold">Discord</a>
             <a href="#" className="text-gray-400 hover:text-white text-sm font-bold">Privacy</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
