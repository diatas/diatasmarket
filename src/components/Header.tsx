import { ShoppingCart, User, LogOut, Store } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useCart } from '../contexts/CartContext';

interface HeaderProps {
  onAuthClick: () => void;
  onCartClick: () => void;
}

export function Header({ onAuthClick, onCartClick }: HeaderProps) {
  const { user, signOut } = useAuth();
  const { cart } = useCart();

  const cartItemsCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <header className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-lg sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Store className="w-8 h-8" />
            <div>
              <h1 className="text-2xl font-bold tracking-tight">DIATAS MARKET</h1>
              <p className="text-xs text-emerald-100">Mode & Chaussures</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <button
              onClick={onCartClick}
              className="relative hover:bg-white/20 p-2 rounded-lg transition-colors"
            >
              <ShoppingCart className="w-6 h-6" />
              {cartItemsCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                  {cartItemsCount}
                </span>
              )}
            </button>

            {user ? (
              <button
                onClick={signOut}
                className="flex items-center space-x-2 hover:bg-white/20 px-4 py-2 rounded-lg transition-colors"
              >
                <LogOut className="w-5 h-5" />
                <span className="hidden sm:inline">Déconnexion</span>
              </button>
            ) : (
              <button
                onClick={onAuthClick}
                className="flex items-center space-x-2 bg-white text-emerald-600 px-4 py-2 rounded-lg font-semibold hover:bg-emerald-50 transition-colors"
              >
                <User className="w-5 h-5" />
                <span className="hidden sm:inline">Connexion</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
