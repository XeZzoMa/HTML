import { useEffect, useMemo, useState } from "react";
import { apiRequest } from "../api/client";

type Ingredient = {
  id: number;
  name: string;
  category: string;
};

export default function IngredientsPage() {
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [name, setName] = useState("");
  const [category, setCategory] = useState("");
  const [filter, setFilter] = useState("");
  const [editing, setEditing] = useState<Ingredient | null>(null);
  const [error, setError] = useState<string | null>(null);

  const categories = useMemo(() => {
    return Array.from(new Set(ingredients.map((item) => item.category))).sort();
  }, [ingredients]);

  async function loadIngredients() {
    const data = await apiRequest<Ingredient[]>("/ingredients");
    setIngredients(data);
  }

  useEffect(() => {
    loadIngredients().catch((err) => setError(err.message || "Failed to load"));
  }, []);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    if (!name || !category) {
      setError("Name and category are required.");
      return;
    }
    try {
      if (editing) {
        await apiRequest(`/ingredients/${editing.id}`, {
          method: "PUT",
          body: JSON.stringify({ name, category }),
        });
      } else {
        await apiRequest("/ingredients", {
          method: "POST",
          body: JSON.stringify({ name, category }),
        });
      }
      setName("");
      setCategory("");
      setEditing(null);
      await loadIngredients();
    } catch (err: any) {
      setError(err.message || "Failed to save");
    }
  }

  function startEdit(item: Ingredient) {
    setEditing(item);
    setName(item.name);
    setCategory(item.category);
  }

  async function removeIngredient(id: number) {
    await apiRequest(`/ingredients/${id}`, { method: "DELETE" });
    await loadIngredients();
  }

  const filtered = ingredients.filter((item) =>
    filter ? item.category.toLowerCase() === filter.toLowerCase() : true
  );

  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold">Add or edit ingredient</h2>
        <form onSubmit={handleSubmit} className="mt-4 grid gap-4 md:grid-cols-3">
          <input
            className="rounded-lg border border-slate-200 px-3 py-2"
            placeholder="Name"
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
          <input
            className="rounded-lg border border-slate-200 px-3 py-2"
            placeholder="Category"
            value={category}
            onChange={(event) => setCategory(event.target.value)}
          />
          <button
            type="submit"
            className="rounded-lg bg-slate-900 px-4 py-2 text-white"
          >
            {editing ? "Update" : "Add"}
          </button>
        </form>
        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      </div>

      <div className="rounded-2xl bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <h2 className="text-lg font-semibold">Ingredients</h2>
          <select
            className="rounded-lg border border-slate-200 px-3 py-2"
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
          >
            <option value="">All categories</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>
        <div className="mt-4 grid gap-3">
          {filtered.map((item) => (
            <div
              key={item.id}
              className="flex flex-wrap items-center justify-between rounded-lg border border-slate-100 px-4 py-3"
            >
              <div>
                <p className="font-medium">{item.name}</p>
                <p className="text-sm text-slate-500">{item.category}</p>
              </div>
              <div className="flex gap-2">
                <button
                  className="rounded-lg border border-slate-200 px-3 py-1 text-sm"
                  onClick={() => startEdit(item)}
                >
                  Edit
                </button>
                <button
                  className="rounded-lg border border-red-200 px-3 py-1 text-sm text-red-600"
                  onClick={() => removeIngredient(item.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
          {filtered.length === 0 && (
            <p className="text-sm text-slate-500">No ingredients yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}
