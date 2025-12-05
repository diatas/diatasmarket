interface Category {
  id: string;
  name: string;
  slug: string;
}

interface CategoryFilterProps {
  categories: Category[];
  selectedCategory: string | null;
  onSelectCategory: (categoryId: string | null) => void;
}

export function CategoryFilter({ categories, selectedCategory, onSelectCategory }: CategoryFilterProps) {
  return (
    <div className="bg-white rounded-2xl shadow-md p-6 mb-8 border border-sky-50">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-bold text-xl text-gray-800">Catégories</h2>
        <span className="text-sm text-sky-600 font-semibold bg-sky-50 px-3 py-1 rounded-full">Filtre rapide</span>
      </div>
      <div className="flex flex-wrap gap-3">
        <button
          onClick={() => onSelectCategory(null)}
          className={`px-5 py-2 rounded-full font-semibold transition-all border ${
            selectedCategory === null
              ? 'bg-sky-600 text-white shadow-lg border-sky-600'
              : 'bg-sky-50 text-sky-700 border-sky-100 hover:border-sky-200 hover:-translate-y-0.5'
          }`}
        >
          Tous les produits
        </button>
        {categories.map((category) => (
          <button
            key={category.id}
            onClick={() => onSelectCategory(category.id)}
            className={`px-5 py-2 rounded-full font-semibold transition-all border ${
              selectedCategory === category.id
                ? 'bg-sky-600 text-white shadow-lg border-sky-600'
                : 'bg-sky-50 text-sky-700 border-sky-100 hover:border-sky-200 hover:-translate-y-0.5'
            }`}
          >
            {category.name}
          </button>
        ))}
      </div>
    </div>
  );
}
