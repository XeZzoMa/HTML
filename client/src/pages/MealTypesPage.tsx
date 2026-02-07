import { useEffect, useState } from "react";
import { apiRequest } from "../api/client";

type MealType = {
  id: number;
  name: string;
};

export default function MealTypesPage() {
  const [mealTypes, setMealTypes] = useState<MealType[]>([]);
  const [name, setName] = useState("");
  const [editing, setEditing] = useState<MealType | null>(null);

  async function loadMealTypes() {
    const data = await apiRequest<MealType[]>("/meal-types");
    setMealTypes(data);
  }

  useEffect(() => {
    loadMealTypes();
  }, []);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!name) return;
    if (editing) {
      await apiRequest(`/meal-types/${editing.id}`, {
        method: "PUT",
        body: JSON.stringify({ name }),
      });
    } else {
      await apiRequest("/meal-types", {
        method: "POST",
        body: JSON.stringify({ name }),
      });
    }
    setName("");
    setEditing(null);
    await loadMealTypes();
  }

  async function removeMealType(id: number) {
    await apiRequest(`/meal-types/${id}`, { method: "DELETE" });
    await loadMealTypes();
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold">Add or edit meal type</h2>
        <form onSubmit={handleSubmit} className="mt-4 flex flex-wrap gap-3">
          <input
            className="flex-1 rounded-lg border border-slate-200 px-3 py-2"
            placeholder="Meal type name"
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
          <button className="rounded-lg bg-slate-900 px-4 py-2 text-white" type="submit">
            {editing ? "Update" : "Add"}
          </button>
        </form>
      </div>

      <div className="rounded-2xl bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold">Meal types</h2>
        <div className="mt-4 space-y-3">
          {mealTypes.map((type) => (
            <div key={type.id} className="flex items-center justify-between rounded-lg border px-4 py-2">
              <span>{type.name}</span>
              <div className="flex gap-2">
                <button
                  className="rounded-lg border border-slate-200 px-3 py-1 text-sm"
                  onClick={() => {
                    setEditing(type);
                    setName(type.name);
                  }}
                >
                  Edit
                </button>
                <button
                  className="rounded-lg border border-red-200 px-3 py-1 text-sm text-red-600"
                  onClick={() => removeMealType(type.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
          {mealTypes.length === 0 && (
            <p className="text-sm text-slate-500">No meal types yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}
