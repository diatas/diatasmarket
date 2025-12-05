import { X, Plus, Minus, Trash2, ShoppingBag } from 'lucide-react';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';

interface CartModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCheckout: () => void;
}

export function CartModal({ isOpen, onClose, onCheckout }: CartModalProps) {
  const { cart, updateQuantity, removeFromCart, getCartTotal } = useCart();
  const { user } = useAuth();

  if (!isOpen) return null;

  const total = getCartTotal();

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-start justify-end">
      <div className="bg-white w-full max-w-md h-full overflow-y-auto shadow-2xl animate-slide-in border-l border-sky-50">
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 z-10">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-800 flex items-center space-x-2">
              <ShoppingBag className="w-6 h-6" />
              <span>Mon Panier</span>
            </h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        <div className="p-6">
          {cart.length === 0 ? (
            <div className="text-center py-12">
              <ShoppingBag className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">Votre panier est vide</p>
            </div>
          ) : (
            <>
              <div className="bg-sky-50 border border-sky-100 rounded-xl p-4 mb-5 flex items-start space-x-3">
                <div className="h-10 w-10 rounded-full bg-white text-sky-600 flex items-center justify-center font-bold shadow-inner">
                  %
                </div>
                <div className="text-sm text-gray-700">
                  <p className="font-semibold text-gray-800">Livraison rapide & retours simples</p>
                  <p className="text-gray-600">Suivi en temps réel et remboursement sous 30 jours si besoin.</p>
                </div>
              </div>

              <div className="space-y-4 mb-6">
                {cart.map((item) => (
                  <div key={item.id} className="bg-gray-50 rounded-lg p-4 flex space-x-4 border border-gray-100">
                    <img
                      src={item.product?.image_url}
                      alt={item.product?.name}
                      className="w-20 h-20 object-cover rounded-lg"
                    />
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-800 mb-1">{item.product?.name}</h3>
                      <p className="text-sm text-gray-600 mb-2">
                        {item.size} • {item.color}
                      </p>
                      <p className="font-bold text-sky-700">
                        {((item.product?.price || 0) * item.quantity).toLocaleString()} FCFA
                      </p>
                    </div>
                    <div className="flex flex-col items-end justify-between">
                      <button
                        onClick={() => removeFromCart(item.id)}
                        className="text-red-500 hover:text-red-700 p-1"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                      <div className="flex items-center space-x-2 bg-white rounded-lg border border-gray-200">
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity - 1)}
                          className="p-1 hover:bg-gray-100 rounded-l-lg"
                        >
                          <Minus className="w-4 h-4" />
                        </button>
                        <span className="px-3 font-semibold">{item.quantity}</span>
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity + 1)}
                          className="p-1 hover:bg-gray-100 rounded-r-lg"
                        >
                          <Plus className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="border-t border-gray-200 pt-6">
                <div className="flex justify-between items-center mb-6">
                  <span className="text-xl font-bold text-gray-800">Total:</span>
                  <span className="text-2xl font-bold text-sky-700">
                    {total.toLocaleString()} FCFA
                  </span>
                </div>

                <div className="bg-sky-50 border border-sky-100 rounded-xl p-4 mb-4 text-sm text-gray-700">
                  <p className="font-semibold text-gray-800 mb-1">Bon à savoir</p>
                  <ul className="list-disc list-inside space-y-1 text-gray-600">
                    <li>Livraison gratuite dès 50.000 FCFA</li>
                    <li>Retours simplifiés sous 30 jours</li>
                    <li>Paiement sécurisé par carte ou mobile money</li>
                  </ul>
                </div>

                {user ? (
                  <button
                    onClick={onCheckout}
                    className="w-full bg-sky-600 text-white py-4 rounded-lg font-bold text-lg hover:bg-sky-700 transition-colors shadow-lg"
                  >
                    Commander
                  </button>
                ) : (
                  <p className="text-center text-gray-600 py-4">
                    Veuillez vous connecter pour commander
                  </p>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
