export interface Database {
  public: {
    Tables: {
      categories: {
        Row: {
          id: string;
          name: string;
          slug: string;
          description: string;
          image_url: string;
          created_at: string;
        };
        Insert: {
          id?: string;
          name: string;
          slug: string;
          description?: string;
          image_url?: string;
          created_at?: string;
        };
        Update: {
          id?: string;
          name?: string;
          slug?: string;
          description?: string;
          image_url?: string;
          created_at?: string;
        };
      };
      products: {
        Row: {
          id: string;
          name: string;
          slug: string;
          description: string;
          price: number;
          category_id: string | null;
          image_url: string;
          images: string[];
          sizes: string[];
          colors: string[];
          stock: number;
          featured: boolean;
          created_at: string;
        };
        Insert: {
          id?: string;
          name: string;
          slug: string;
          description?: string;
          price: number;
          category_id?: string | null;
          image_url?: string;
          images?: string[];
          sizes?: string[];
          colors?: string[];
          stock?: number;
          featured?: boolean;
          created_at?: string;
        };
        Update: {
          id?: string;
          name?: string;
          slug?: string;
          description?: string;
          price?: number;
          category_id?: string | null;
          image_url?: string;
          images?: string[];
          sizes?: string[];
          colors?: string[];
          stock?: number;
          featured?: boolean;
          created_at?: string;
        };
      };
      cart: {
        Row: {
          id: string;
          user_id: string;
          product_id: string;
          quantity: number;
          size: string;
          color: string;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          product_id: string;
          quantity: number;
          size?: string;
          color?: string;
          created_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          product_id?: string;
          quantity?: number;
          size?: string;
          color?: string;
          created_at?: string;
        };
      };
      orders: {
        Row: {
          id: string;
          user_id: string;
          total_amount: number;
          payment_method: string;
          payment_status: string;
          delivery_address: {
            name: string;
            phone: string;
            address: string;
            city: string;
          };
          status: string;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          total_amount: number;
          payment_method: string;
          payment_status?: string;
          delivery_address?: object;
          status?: string;
          created_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          total_amount?: number;
          payment_method?: string;
          payment_status?: string;
          delivery_address?: object;
          status?: string;
          created_at?: string;
        };
      };
      order_items: {
        Row: {
          id: string;
          order_id: string;
          product_id: string | null;
          quantity: number;
          size: string;
          color: string;
          price: number;
          created_at: string;
        };
        Insert: {
          id?: string;
          order_id: string;
          product_id?: string | null;
          quantity: number;
          size?: string;
          color?: string;
          price: number;
          created_at?: string;
        };
        Update: {
          id?: string;
          order_id?: string;
          product_id?: string | null;
          quantity?: number;
          size?: string;
          color?: string;
          price?: number;
          created_at?: string;
        };
      };
    };
  };
}
