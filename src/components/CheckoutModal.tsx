import { X, CreditCard, Smartphone, CheckCircle } from 'lucide-react';
import { useState } from 'react';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';
import { supabase, isSupabaseConfigured } from '../lib/supabase';

interface CheckoutModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const paymentMethods = [
  { id: 'orange-money', name: 'Orange Money', icon: Smartphone },
  { id: 'mobile-money', name: 'Mobile Money', icon: Smartphone },
  { id: 'paycard', name: 'Paycard', icon: CreditCard },
  { id: 'visa', name: 'Visa Card', icon: CreditCard },
  { id: 'mastercard', name: 'Mastercard', icon: CreditCard },
];

export function CheckoutModal({ isOpen, onClose }: CheckoutModalProps) {
  const [selectedPayment, setSelectedPayment] = useState('');
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [city, setCity] = useState('');
  const [loading, setLoading] = useState(false);
  const [orderComplete, setOrderComplete] = useState(false);
  const { cart, getCartTotal, clearCart } = useCart();
  const { user } = useAuth();

  if (!isOpen) return null;

  const total = getCartTotal();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    setLoading(true);

    try {
      if (!supabase) {
        throw new Error('Supabase n’est pas configuré.');
      }

      const { data: order, error: orderError } = await supabase
        .from('orders')
        .insert({
          user_id: user.id,
          total_amount: total,
          payment_method: selectedPayment,
          payment_status: 'pending',
          delivery_address: { name, phone, address, city },
          status: 'pending',
        })
        .select()
        .single();

      if (orderError) throw orderError;

      const orderItems = cart.map((item) => ({
        order_id: order.id,
        product_id: item.product_id,
        quantity: item.quantity,
        size: item.size,
        color: item.color,
        price: item.product?.price || 0,
      }));

      const { error: itemsError } = await supabase
        .from('order_items')
        .insert(orderItems);

      if (itemsError) throw itemsError;

      await clearCart();
      setOrderComplete(true);

      setTimeout(() => {
        onClose();
        setOrderComplete(false);
        setName('');
        setPhone('');
        setAddress('');
        setCity('');
        setSelectedPayment('');
      }, 3000);
    } catch (error) {
      console.error('Error creating order:', error);
    } finally {
      setLoading(false);
    }
  };

  if (orderComplete) {
    return (
      <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl max-w-md w-full p-8 text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Commande confirmée!</h2>
          <p className="text-gray-600">Merci pour votre commande. Nous vous contacterons bientôt.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl max-w-2xl w-full p-8 relative my-8 border border-sky-50 shadow-2xl">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-500 hover:text-gray-700 p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <h2 className="text-2xl font-bold text-gray-800 mb-2">Finaliser la commande</h2>
        <p className="text-sm text-gray-500 mb-4">Livraison sécurisée avec suivi email.</p>

        {!isSupabaseConfigured && (
          <div className="mb-6 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
            <p className="font-semibold">Supabase n’est pas configuré.</p>
            <p>Ajoutez vos variables d’environnement pour activer la création de commande.</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="bg-sky-50 rounded-lg p-4 border border-sky-100">
            <h3 className="font-semibold text-gray-800 mb-3">Récapitulatif</h3>
            <div className="space-y-2">
              {cart.map((item) => (
                <div key={item.id} className="flex justify-between text-sm">
                  <span className="text-gray-600">
                    {item.product?.name} x{item.quantity}
                  </span>
                  <span className="font-semibold text-gray-800">
                    {((item.product?.price || 0) * item.quantity).toLocaleString()} FCFA
                  </span>
                </div>
              ))}
              <div className="border-t border-gray-200 pt-2 mt-2 flex justify-between">
                <span className="font-bold text-gray-800">Total:</span>
                <span className="font-bold text-sky-700 text-lg">
                  {total.toLocaleString()} FCFA
                </span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-gray-800 mb-3">Informations de livraison</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                placeholder="Nom complet"
                className="px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-sky-500 focus:border-transparent outline-none"
              />
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                required
                placeholder="Téléphone"
                className="px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-sky-500 focus:border-transparent outline-none"
              />
              <input
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                required
                placeholder="Adresse"
                className="px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-sky-500 focus:border-transparent outline-none md:col-span-2"
              />
              <input
                type="text"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                required
                placeholder="Ville"
                className="px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-sky-500 focus:border-transparent outline-none md:col-span-2"
              />
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-gray-800 mb-3">Méthode de paiement</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {paymentMethods.map((method) => {
                const Icon = method.icon;
                return (
                  <button
                    key={method.id}
                    type="button"
                    onClick={() => setSelectedPayment(method.id)}
                    className={`flex items-center space-x-3 p-4 rounded-lg border-2 transition-all ${
                      selectedPayment === method.id
                        ? 'border-sky-600 bg-sky-50 shadow'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="w-6 h-6 text-sky-600" />
                    <span className="font-medium text-gray-800">{method.name}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !selectedPayment || !isSupabaseConfigured}
            className="w-full bg-sky-600 text-white py-4 rounded-lg font-bold text-lg hover:bg-sky-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow"
          >
            {loading ? 'Traitement...' : 'Confirmer la commande'}
          </button>
        </form>
      </div>
    </div>
  );
}
