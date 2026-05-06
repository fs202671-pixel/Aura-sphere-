import React, { useEffect, useState } from 'react';
import { Search, Download, Maximize2 } from 'lucide-react';

interface ImageReference {
  id: string;
  url: string;
  title: string;
  author: string;
  description: string;
}

export function ThemeGallery() {
  const [searchQuery, setSearchQuery] = useState('');
  const [images, setImages] = useState<ImageReference[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState<ImageReference | null>(null);

  // Mock de imagens de referência
  const mockImages: Record<string, ImageReference[]> = {
    'default': [
      {
        id: '1',
        url: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400',
        title: 'Sunset',
        author: 'John Doe',
        description: 'Beautiful sunset over the mountains'
      },
      {
        id: '2',
        url: 'https://images.unsplash.com/photo-1505142468610-359e7d316be0?w=400',
        title: 'Ocean Waves',
        author: 'Jane Smith',
        description: 'Ocean waves crashing against the shore'
      },
      {
        id: '3',
        url: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400',
        title: 'Forest',
        author: 'Bob Johnson',
        description: 'Dense forest with sunlight'
      }
    ],
    'dark': [
      {
        id: '4',
        url: 'https://images.unsplash.com/photo-1444080748397-f442aa95c3e5?w=400',
        title: 'Night Sky',
        author: 'Alice Brown',
        description: 'Stars in the night sky'
      },
      {
        id: '5',
        url: 'https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=400',
        title: 'Northern Lights',
        author: 'Charlie White',
        description: 'Aurora borealis'
      }
    ],
    'nature': [
      {
        id: '6',
        url: 'https://images.unsplash.com/photo-1495107212441-d9de3f3cc628?w=400',
        title: 'Mountain Peak',
        author: 'David Miller',
        description: 'Snowy mountain peak'
      },
      {
        id: '7',
        url: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400',
        title: 'Green Forest',
        author: 'Eve Taylor',
        description: 'Lush green forest'
      }
    ],
    'technology': [
      {
        id: '8',
        url: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400',
        title: 'Digital',
        author: 'Frank Anderson',
        description: 'Digital abstract art'
      },
      {
        id: '9',
        url: 'https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=400',
        title: 'Code',
        author: 'Grace Lee',
        description: 'Code on screen'
      }
    ]
  };

  const searchImages = async (query: string) => {
    setLoading(true);
    
    // Simular busca em API
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const results = mockImages[query.toLowerCase()] || mockImages['default'];
    setImages(results);
    setLoading(false);
  };

  useEffect(() => {
    searchImages('default');
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      searchImages(searchQuery);
    }
  };

  const downloadImage = (image: ImageReference) => {
    // Simular download
    alert(`Imagem "${image.title}" baixada!\n\nURL: ${image.url}`);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold text-white">Galeria de Referências de Tema</h2>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="text"
          placeholder="Busque temas: dark, nature, technology, default..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 bg-slate-800 border border-slate-600 text-white px-4 py-2 rounded-lg placeholder:text-slate-500"
        />
        <button
          type="submit"
          className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition"
        >
          <Search className="w-4 h-4" />
          Buscar
        </button>
      </form>

      {/* Image Grid */}
      {loading ? (
        <div className="text-center text-slate-300">Carregando imagens...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {images.map((image) => (
            <div
              key={image.id}
              className="group relative bg-slate-700/50 border border-slate-600 rounded-lg overflow-hidden hover:border-blue-500 transition cursor-pointer"
              onClick={() => setSelectedImage(image)}
            >
              {/* Image Placeholder */}
              <div className="w-full h-48 bg-gradient-to-br from-slate-600 to-slate-800 flex items-center justify-center">
                <div
                  className="w-full h-full text-center p-4 flex flex-col items-center justify-center text-white opacity-50"
                >
                  <Maximize2 className="w-8 h-8 mb-2" />
                  <p className="text-sm">{image.title}</p>
                </div>
              </div>

              {/* Info */}
              <div className="p-4 bg-slate-800/80 backdrop-blur">
                <h3 className="text-white font-semibold">{image.title}</h3>
                <p className="text-sm text-slate-400">{image.author}</p>
                <p className="text-xs text-slate-500 mt-2">{image.description}</p>
              </div>

              {/* Hover Actions */}
              <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition flex items-center justify-center gap-3">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedImage(image);
                  }}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded font-semibold"
                >
                  <Maximize2 className="w-4 h-4" />
                  Visualizar
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    downloadImage(image);
                  }}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded font-semibold"
                >
                  <Download className="w-4 h-4" />
                  Usar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {selectedImage && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur z-50 flex items-center justify-center p-4">
          <div className="bg-slate-800 border border-slate-600 rounded-lg max-w-2xl w-full p-6 space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-2xl font-bold text-white">{selectedImage.title}</h3>
              <button
                onClick={() => setSelectedImage(null)}
                className="text-3xl text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            {/* Image Placeholder */}
            <div className="w-full h-64 bg-gradient-to-br from-slate-600 to-slate-800 rounded flex items-center justify-center">
              <Maximize2 className="w-16 h-16 text-slate-500 opacity-50" />
            </div>

            <div className="space-y-2">
              <p className="text-sm text-slate-300">
                <span className="text-slate-400">Autor:</span> {selectedImage.author}
              </p>
              <p className="text-sm text-slate-300">
                <span className="text-slate-400">Descrição:</span> {selectedImage.description}
              </p>
              <p className="text-xs text-slate-500">
                URL: <span className="font-mono">{selectedImage.url}</span>
              </p>
            </div>

            <div className="flex gap-3 pt-4">
              <button
                onClick={() => downloadImage(selectedImage)}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition"
              >
                <Download className="w-4 h-4" />
                Usar como Background
              </button>
              <button
                onClick={() => setSelectedImage(null)}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-semibold transition"
              >
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
