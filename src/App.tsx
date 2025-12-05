import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { ProductCard } from './components/ProductCard';
import { CategoryFilter } from './components/CategoryFilter';
import { CartModal } from './components/CartModal';
import { AuthModal } from './components/AuthModal';
import { CheckoutModal } from './components/CheckoutModal';
import { useAuth } from './contexts/AuthContext';
import { useCart } from './contexts/CartContext';
import { supabase } from './lib/supabase';

interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  image_url: string;
  sizes: string[];
  colors: string[];
  stock: number;
  category_id: string | null;
}

interface Category {
  id: string;
  name: string;
  slug: string;
}

function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [cartModalOpen, setCartModalOpen] = useState(false);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [checkoutModalOpen, setCheckoutModalOpen] = useState(false);
  const { addToCart } = useCart();
  const { user } = useAuth();

  useEffect(() => {
    fetchCategories();
    fetchProducts();
  }, [selectedCategory]);

  const fetchCategories = async () => {
    const { data } = await supabase
      .from('categories')
      .select('*')
      .order('name');

    if (data) {
      setCategories(data);
    }
  };

  const fetchProducts = async () => {
    setLoading(true);
    let query = supabase
      .from('products')
      .select('*')
      .order('created_at', { ascending: false });

    if (selectedCategory) {
      query = query.eq('category_id', selectedCategory);
    }

    const { data } = await query;

    if (data) {
      setProducts(data);
    }
    setLoading(false);
  };

  const handleAddToCart = async (productId: string, size: string, color: string) => {
    if (!user) {
      setAuthModalOpen(true);
      return;
    }

    await addToCart(productId, 1, size, color);
  };

  const handleCheckout = () => {
    setCartModalOpen(false);
    setCheckoutModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-blue-50">
      <Header
        onAuthClick={() => setAuthModalOpen(true)}
        onCartClick={() => setCartModalOpen(true)}
      />

      <main className="container mx-auto px-4 py-8">
        <div className="mb-8 grid lg:grid-cols-[2fr,1fr] gap-6 items-center">
          <div className="bg-gradient-to-r from-sky-500 via-sky-400 to-blue-500 text-white rounded-3xl p-10 shadow-xl relative overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,_rgba(255,255,255,0.18),_transparent_40%),_radial-gradient(circle_at_80%_0%,_rgba(255,255,255,0.14),_transparent_35%)]" />
            <div className="relative z-10 space-y-4">
              <p className="uppercase tracking-[0.2em] text-xs font-semibold text-sky-50/90">Nouvelle saison</p>
              <h2 className="text-4xl font-bold leading-tight">Bienvenue chez DIATAS MARKET</h2>
              <p className="text-lg text-sky-50/90 max-w-2xl">
                Explorez notre sélection de vêtements et chaussures avec des offres exclusives, livraisons rapides et retours simplifiés.
              </p>
              <div className="flex flex-wrap gap-3 pt-2">
                <button className="bg-white text-sky-600 font-bold px-5 py-3 rounded-xl shadow-lg hover:-translate-y-0.5 transition-transform">
                  Découvrir la collection
                </button>
                <button className="border border-white/50 text-white font-semibold px-5 py-3 rounded-xl hover:bg-white/10 transition-colors">
                  Voir les nouveautés
                </button>
              </div>
              <div className="flex flex-wrap gap-4 pt-4 text-sm text-sky-50/90">
                <span className="px-4 py-2 bg-white/10 rounded-full border border-white/20">Livraison offerte dès 50.000 FCFA</span>
                <span className="px-4 py-2 bg-white/10 rounded-full border border-white/20">Retours faciles sous 30 jours</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-3xl p-6 shadow-lg border border-sky-50">
            <h3 className="text-xl font-bold text-gray-800 mb-2">Préparez votre look</h3>
            <p className="text-gray-600 mb-4">
              Filtrez par catégorie pour trouver rapidement vos essentiels. Couleurs et tailles sont disponibles sur chaque fiche produit.
            </p>
            <div className="space-y-3 text-sm">
              <div className="flex items-center space-x-3">
                <span className="h-10 w-10 rounded-xl bg-sky-100 text-sky-600 font-bold flex items-center justify-center">1</span>
                <div>
                  <p className="font-semibold text-gray-800">Choisissez une catégorie</p>
                  <p className="text-gray-600">Découvrir les produits qui vous intéressent en priorité.</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <span className="h-10 w-10 rounded-xl bg-sky-100 text-sky-600 font-bold flex items-center justify-center">2</span>
                <div>
                  <p className="font-semibold text-gray-800">Personnalisez</p>
                  <p className="text-gray-600">Sélectionnez taille et couleur avant d’ajouter au panier.</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <span className="h-10 w-10 rounded-xl bg-sky-100 text-sky-600 font-bold flex items-center justify-center">3</span>
                <div>
                  <p className="font-semibold text-gray-800">Commandez sereinement</p>
                  <p className="text-gray-600">Paiement sécurisé et suivi par email.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <CategoryFilter
          categories={categories}
          selectedCategory={selectedCategory}
          onSelectCategory={setSelectedCategory}
        />

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6" aria-label="Chargement des produits">
            {Array.from({ length: 8 }).map((_, index) => (
              <div
                key={index}
                className="bg-white rounded-xl shadow-md overflow-hidden animate-pulse border border-sky-50"
              >
                <div className="h-64 bg-sky-100" />
                <div className="p-5 space-y-3">
                  <div className="h-4 bg-sky-100 rounded w-3/4" />
                  <div className="h-3 bg-sky-100 rounded w-full" />
                  <div className="h-3 bg-sky-100 rounded w-5/6" />
                  <div className="flex gap-2 pt-2">
                    <span className="h-8 w-16 bg-sky-100 rounded-lg" />
                    <span className="h-8 w-16 bg-sky-100 rounded-lg" />
                  </div>
                  <div className="flex items-center justify-between pt-4">
                    <span className="h-6 w-24 bg-sky-100 rounded" />
                    <span className="h-10 w-24 bg-sky-100 rounded-lg" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {products.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onAddToCart={handleAddToCart}
              />
            ))}
          </div>
        )}

        {!loading && products.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">Aucun produit disponible</p>
          </div>
        )}
      </main>

      <footer className="bg-gray-900 text-white py-10 mt-16">
        <div className="container mx-auto px-4 grid md:grid-cols-3 gap-8">
          <div>
            <p className="text-lg font-semibold mb-2">DIATAS MARKET</p>
            <p className="text-gray-400 text-sm">Votre destination pour la mode et les chaussures.</p>
            <p className="text-gray-400 text-sm mt-3">Livraison rapide, retours simplifiés et paiement sécurisé.</p>
          </div>
          <div>
            <p className="text-lg font-semibold mb-3">Support</p>
            <ul className="space-y-2 text-gray-400 text-sm">
              <li>FAQ & retours</li>
              <li>Contact: support@diatasmarket.com</li>
              <li>Suivi de commande</li>
            </ul>
          </div>
          <div>
            <p className="text-lg font-semibold mb-3">Réseaux</p>
            <ul className="space-y-2 text-gray-400 text-sm">
              <li>Instagram</li>
              <li>Facebook</li>
              <li>TikTok</li>
            </ul>
          </div>
        </div>
      </footer>

      <CartModal
        isOpen={cartModalOpen}
        onClose={() => setCartModalOpen(false)}
        onCheckout={handleCheckout}
      />

      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
      />

      <CheckoutModal
        isOpen={checkoutModalOpen}
        onClose={() => setCheckoutModalOpen(false)}
      />
    </div>
  );
}

export default App;
