/*
  # Create DIATAS MARKET E-commerce Schema

  1. New Tables
    - `categories`
      - `id` (uuid, primary key)
      - `name` (text, category name)
      - `slug` (text, URL-friendly name)
      - `description` (text, optional)
      - `image_url` (text, category image)
      - `created_at` (timestamp)
    
    - `products`
      - `id` (uuid, primary key)
      - `name` (text, product name)
      - `slug` (text, URL-friendly name)
      - `description` (text)
      - `price` (numeric, product price)
      - `category_id` (uuid, foreign key to categories)
      - `image_url` (text, main product image)
      - `images` (jsonb, array of additional images)
      - `sizes` (jsonb, available sizes)
      - `colors` (jsonb, available colors)
      - `stock` (integer, quantity in stock)
      - `featured` (boolean, featured product)
      - `created_at` (timestamp)
    
    - `cart`
      - `id` (uuid, primary key)
      - `user_id` (uuid, foreign key to auth.users)
      - `product_id` (uuid, foreign key to products)
      - `quantity` (integer)
      - `size` (text, selected size)
      - `color` (text, selected color)
      - `created_at` (timestamp)
    
    - `orders`
      - `id` (uuid, primary key)
      - `user_id` (uuid, foreign key to auth.users)
      - `total_amount` (numeric)
      - `payment_method` (text)
      - `payment_status` (text)
      - `delivery_address` (jsonb)
      - `status` (text)
      - `created_at` (timestamp)
    
    - `order_items`
      - `id` (uuid, primary key)
      - `order_id` (uuid, foreign key to orders)
      - `product_id` (uuid, foreign key to products)
      - `quantity` (integer)
      - `size` (text)
      - `color` (text)
      - `price` (numeric)
      - `created_at` (timestamp)

  2. Security
    - Enable RLS on all tables
    - Add policies for authenticated and public access where appropriate
*/

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  slug text UNIQUE NOT NULL,
  description text DEFAULT '',
  image_url text DEFAULT '',
  created_at timestamptz DEFAULT now()
);

ALTER TABLE categories ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view categories"
  ON categories FOR SELECT
  TO public
  USING (true);

-- Products table
CREATE TABLE IF NOT EXISTS products (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  slug text UNIQUE NOT NULL,
  description text DEFAULT '',
  price numeric NOT NULL CHECK (price >= 0),
  category_id uuid REFERENCES categories(id) ON DELETE SET NULL,
  image_url text DEFAULT '',
  images jsonb DEFAULT '[]'::jsonb,
  sizes jsonb DEFAULT '[]'::jsonb,
  colors jsonb DEFAULT '[]'::jsonb,
  stock integer DEFAULT 0 CHECK (stock >= 0),
  featured boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE products ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view products"
  ON products FOR SELECT
  TO public
  USING (true);

-- Cart table
CREATE TABLE IF NOT EXISTS cart (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  product_id uuid REFERENCES products(id) ON DELETE CASCADE NOT NULL,
  quantity integer NOT NULL CHECK (quantity > 0),
  size text DEFAULT '',
  color text DEFAULT '',
  created_at timestamptz DEFAULT now(),
  UNIQUE(user_id, product_id, size, color)
);

ALTER TABLE cart ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own cart"
  ON cart FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert into own cart"
  ON cart FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own cart"
  ON cart FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete from own cart"
  ON cart FOR DELETE
  TO authenticated
  USING (auth.uid() = user_id);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  total_amount numeric NOT NULL CHECK (total_amount >= 0),
  payment_method text NOT NULL,
  payment_status text DEFAULT 'pending',
  delivery_address jsonb DEFAULT '{}'::jsonb,
  status text DEFAULT 'pending',
  created_at timestamptz DEFAULT now()
);

ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own orders"
  ON orders FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own orders"
  ON orders FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

-- Order items table
CREATE TABLE IF NOT EXISTS order_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id uuid REFERENCES orders(id) ON DELETE CASCADE NOT NULL,
  product_id uuid REFERENCES products(id) ON DELETE SET NULL,
  quantity integer NOT NULL CHECK (quantity > 0),
  size text DEFAULT '',
  color text DEFAULT '',
  price numeric NOT NULL CHECK (price >= 0),
  created_at timestamptz DEFAULT now()
);

ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own order items"
  ON order_items FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM orders
      WHERE orders.id = order_items.order_id
      AND orders.user_id = auth.uid()
    )
  );

-- Insert sample categories
INSERT INTO categories (name, slug, description, image_url) VALUES
  ('Vêtements Homme', 'vetements-homme', 'Collection de vêtements pour hommes', 'https://images.pexels.com/photos/1020585/pexels-photo-1020585.jpeg'),
  ('Vêtements Femme', 'vetements-femme', 'Collection de vêtements pour femmes', 'https://images.pexels.com/photos/972995/pexels-photo-972995.jpeg'),
  ('Chaussures Homme', 'chaussures-homme', 'Collection de chaussures pour hommes', 'https://images.pexels.com/photos/1598505/pexels-photo-1598505.jpeg'),
  ('Chaussures Femme', 'chaussures-femme', 'Collection de chaussures pour femmes', 'https://images.pexels.com/photos/336372/pexels-photo-336372.jpeg')
ON CONFLICT (slug) DO NOTHING;

-- Insert sample products
INSERT INTO products (name, slug, description, price, category_id, image_url, sizes, colors, stock, featured) 
SELECT 
  'T-shirt Premium Homme',
  't-shirt-premium-homme',
  'T-shirt en coton de qualité supérieure, confortable et élégant',
  15000,
  id,
  'https://images.pexels.com/photos/1656684/pexels-photo-1656684.jpeg',
  '["S", "M", "L", "XL", "XXL"]'::jsonb,
  '["Noir", "Blanc", "Bleu", "Gris"]'::jsonb,
  50,
  true
FROM categories WHERE slug = 'vetements-homme'
ON CONFLICT (slug) DO NOTHING;

INSERT INTO products (name, slug, description, price, category_id, image_url, sizes, colors, stock, featured)
SELECT 
  'Robe Élégante',
  'robe-elegante',
  'Robe élégante parfaite pour toutes les occasions',
  35000,
  id,
  'https://images.pexels.com/photos/985635/pexels-photo-985635.jpeg',
  '["S", "M", "L", "XL"]'::jsonb,
  '["Rouge", "Noir", "Bleu Marine"]'::jsonb,
  30,
  true
FROM categories WHERE slug = 'vetements-femme'
ON CONFLICT (slug) DO NOTHING;

INSERT INTO products (name, slug, description, price, category_id, image_url, sizes, colors, stock, featured)
SELECT 
  'Baskets Sport Homme',
  'baskets-sport-homme',
  'Baskets confortables pour le sport et le quotidien',
  45000,
  id,
  'https://images.pexels.com/photos/2529148/pexels-photo-2529148.jpeg',
  '["39", "40", "41", "42", "43", "44", "45"]'::jsonb,
  '["Noir", "Blanc", "Bleu"]'::jsonb,
  40,
  true
FROM categories WHERE slug = 'chaussures-homme'
ON CONFLICT (slug) DO NOTHING;

INSERT INTO products (name, slug, description, price, category_id, image_url, sizes, colors, stock, featured)
SELECT 
  'Escarpins Femme',
  'escarpins-femme',
  'Escarpins élégants pour un look sophistiqué',
  38000,
  id,
  'https://images.pexels.com/photos/336372/pexels-photo-336372.jpeg',
  '["36", "37", "38", "39", "40", "41"]'::jsonb,
  '["Noir", "Rouge", "Beige"]'::jsonb,
  25,
  true
FROM categories WHERE slug = 'chaussures-femme'
ON CONFLICT (slug) DO NOTHING;