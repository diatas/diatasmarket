import { ShoppingBag } from 'lucide-react';
import { useState } from 'react';

interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  image_url: string;
  sizes: string[];
  colors: string[];
  stock: number;
}

interface ProductCardProps {
  product: Product;
  onAddToCart: (productId: string, size: string, color: string) => void;
}

export function ProductCard({ product, onAddToCart }: ProductCardProps) {
  const [selectedSize, setSelectedSize] = useState(product.sizes[0] || '');
  const [selectedColor, setSelectedColor] = useState(product.colors[0] || '');

  const handleAddToCart = () => {
    if (selectedSize && selectedColor) {
      onAddToCart(product.id, selectedSize, selectedColor);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-md overflow-hidden hover:shadow-2xl transition-shadow duration-300 border border-sky-50">
      <div className="relative h-64 overflow-hidden bg-gradient-to-b from-sky-50 to-white">
        <img
          src={product.image_url}
          alt={product.name}
          className="w-full h-full object-cover hover:scale-110 transition-transform duration-500"
        />
        {product.stock < 10 && product.stock > 0 && (
          <span className="absolute top-3 right-3 bg-orange-500 text-white px-3 py-1 rounded-full text-xs font-semibold shadow">
            Stock limité
          </span>
        )}
        {product.stock === 0 && (
          <span className="absolute top-3 right-3 bg-red-500 text-white px-3 py-1 rounded-full text-xs font-semibold shadow">
            Épuisé
          </span>
        )}
        <div className="absolute bottom-3 left-3 bg-white/90 backdrop-blur rounded-full px-3 py-1 text-xs font-semibold text-sky-600 shadow">
          Livraison rapide • Retours 30j
        </div>
      </div>

      <div className="p-5">
        <h3 className="font-bold text-lg text-gray-900 mb-2 line-clamp-1">{product.name}</h3>
        <p className="text-gray-600 text-sm mb-3 line-clamp-2">{product.description}</p>
        <div className="flex items-center gap-2 mb-4">
          <span className="px-3 py-1 rounded-full bg-sky-50 text-sky-700 text-xs font-semibold">Nouveauté</span>
          <span className="px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold">Satisfait ou remboursé</span>
        </div>

        <div className="mb-4">
          <label className="text-sm font-semibold text-gray-800 mb-2 block">Taille:</label>
          <div className="flex flex-wrap gap-2">
            {product.sizes.map((size) => (
              <button
                key={size}
                onClick={() => setSelectedSize(size)}
                className={`px-3 py-1 rounded-md text-sm font-semibold transition-all border ${
                  selectedSize === size
                    ? 'bg-sky-600 text-white border-sky-600 shadow'
                    : 'bg-sky-50 text-sky-700 border-sky-100 hover:border-sky-200 hover:-translate-y-0.5'
                }`}
              >
                {size}
              </button>
            ))}
          </div>
        </div>

        <div className="mb-4">
          <label className="text-sm font-semibold text-gray-800 mb-2 block">Couleur:</label>
          <div className="flex flex-wrap gap-2">
            {product.colors.map((color) => (
              <button
                key={color}
                onClick={() => setSelectedColor(color)}
                className={`px-3 py-1 rounded-md text-sm font-semibold transition-all border ${
                  selectedColor === color
                    ? 'bg-sky-600 text-white border-sky-600 shadow'
                    : 'bg-sky-50 text-sky-700 border-sky-100 hover:border-sky-200 hover:-translate-y-0.5'
                }`}
              >
                {color}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-2xl font-bold text-sky-700">{product.price.toLocaleString()} FCFA</span>
          <button
            onClick={handleAddToCart}
            disabled={product.stock === 0}
            className="bg-sky-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-sky-700 transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed shadow"
          >
            <ShoppingBag className="w-5 h-5" />
            <span>Ajouter</span>
          </button>
        </div>
      </div>
    </div>
  );
}
