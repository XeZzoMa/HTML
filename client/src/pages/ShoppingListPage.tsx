import { useEffect, useMemo, useState } from "react";
import { apiRequest } from "../api/client";

type ShoppingItem = {
  item_key: string;
  name: string;
  category: string | null;
  quantity: number | null;
  unit: string | null;
  checked: boolean;
  source: string;
};

type ShoppingListResponse = {
  untilDate: string;
  items: ShoppingItem[];
};

type Shop = { id: number; name: string };

export default function ShoppingListPage() {
  const [items, setItems] = useState<ShoppingItem[]>([]);
  const [untilDate, setUntilDate] = useState<string>("");
  const [shops, setShops] = useState<Shop[]>([]);
  const [shopId, setShopId] = useState<number | "">("");
  const [customName, setCustomName] = useState("");
  const [customCategory, setCustomCategory] = useState("");
  const [customQuantity, setCustomQuantity] = useState("");
  const [customUnit, setCustomUnit] = useState("");
  const [newShopName, setNewShopName] = useState("");
  const [uncheckSequence, setUncheckSequence] = useState<string[]>([]);

  async function loadShops() {
    const data = await apiRequest<Shop[]>("/shops");
    setShops(data);
  }

  async function loadShoppingList(dateOverride?: string, shopOverride?: number | "") {
    const dateParam = dateOverride ?? untilDate;
    const shopParam = shopOverride ?? shopId;
    const params = new URLSearchParams();
    if (dateParam) params.append("untilDate", dateParam);
    if (shopParam) params.append("shopId", String(shopParam));
    const data = await apiRequest<ShoppingListResponse>(`/shopping-list?${params.toString()}`);
    setItems(data.items);
    setUntilDate(data.untilDate);
  }

  useEffect(() => {
    Promise.all([loadShops(), loadShoppingList()]);
  }, []);

  async function addCustomItem(event: React.FormEvent) {
    event.preventDefault();
    if (!customName) return;
    await apiRequest("/shopping-list/custom-item", {
      method: "POST",
      body: JSON.stringify({
        name: customName,
        category: customCategory || null,
        quantity: customQuantity ? Number(customQuantity) : null,
        unit: customUnit || null,
      }),
    });
    setCustomName("");
    setCustomCategory("");
    setCustomQuantity("");
    setCustomUnit("");
    await loadShoppingList();
  }

  async function toggleItem(item: ShoppingItem) {
    const nextChecked = !item.checked;
    await apiRequest("/shopping-list/toggle", {
      method: "POST",
      body: JSON.stringify({ item_key: item.item_key, checked: nextChecked }),
    });
    if (!nextChecked) {
      setUncheckSequence((prev) => [...prev, item.item_key]);
    }
    await loadShoppingList();
  }

  async function saveLearnedOrder() {
    if (!shopId || uncheckSequence.length === 0) return;
    await apiRequest("/shopping-list/learn-order", {
      method: "POST",
      body: JSON.stringify({ shopId, itemKeys: uncheckSequence }),
    });
    setUncheckSequence([]);
    await loadShoppingList();
  }

  async function addShop() {
    if (!newShopName) return;
    await apiRequest("/shops", {
      method: "POST",
      body: JSON.stringify({ name: newShopName }),
    });
    setNewShopName("");
    await loadShops();
  }

  const checkedItems = useMemo(() => items.filter((item) => item.checked), [items]);
  const uncheckedItems = useMemo(() => items.filter((item) => !item.checked), [items]);

  function formatQuantity(item: ShoppingItem) {
    if (item.quantity === null) return "";
    const value = item.quantity.toFixed(2).replace(/\.00$/, "");
    return `${value} ${item.unit || ""}`.trim();
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold">Shopping list</h2>
        <div className="mt-4 flex flex-wrap gap-4">
          <div className="flex flex-col gap-2">
            <label className="text-sm text-slate-500">Until date</label>
            <input
              type="date"
              value={untilDate}
              onChange={(event) => {
                setUntilDate(event.target.value);
                loadShoppingList(event.target.value);
              }}
              className="rounded-lg border border-slate-200 px-3 py-2"
            />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-sm text-slate-500">Shop</label>
            <select
              className="rounded-lg border border-slate-200 px-3 py-2"
              value={shopId}
              onChange={(event) => {
                const value = event.target.value ? Number(event.target.value) : "";
                setShopId(value);
                loadShoppingList(undefined, value);
              }}
            >
              <option value="">No shop</option>
              {shops.map((shop) => (
                <option key={shop.id} value={shop.id}>
                  {shop.name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-sm text-slate-500">Add shop</label>
            <div className="flex gap-2">
              <input
                className="rounded-lg border border-slate-200 px-3 py-2"
                placeholder="New shop"
                value={newShopName}
                onChange={(event) => setNewShopName(event.target.value)}
              />
              <button className="rounded-lg bg-slate-900 px-3 py-2 text-white" onClick={addShop}>
                Add
              </button>
            </div>
          </div>
        </div>

        <div className="mt-6">
          <h3 className="font-medium">Items to buy</h3>
          <div className="mt-2 space-y-2">
            {uncheckedItems.map((item) => (
              <div
                key={item.item_key}
                className="flex items-center justify-between rounded-lg border border-slate-100 px-4 py-3"
              >
                <div>
                  <p className="font-medium">{item.name}</p>
                  <p className="text-sm text-slate-500">
                    {item.category || "Uncategorized"} · {formatQuantity(item) || "No quantity"}
                  </p>
                </div>
                <button
                  className="rounded-full border border-slate-200 px-3 py-1 text-sm"
                  onClick={() => toggleItem(item)}
                >
                  Check
                </button>
              </div>
            ))}
            {uncheckedItems.length === 0 && (
              <p className="text-sm text-slate-500">All items checked.</p>
            )}
          </div>
        </div>

        <div className="mt-6">
          <h3 className="font-medium">Checked</h3>
          <div className="mt-2 space-y-2">
            {checkedItems.map((item) => (
              <div
                key={item.item_key}
                className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50 px-4 py-3 text-slate-400"
              >
                <div>
                  <p className="font-medium line-through">{item.name}</p>
                  <p className="text-sm">
                    {item.category || "Uncategorized"} · {formatQuantity(item) || "No quantity"}
                  </p>
                </div>
                <button
                  className="rounded-full border border-slate-200 px-3 py-1 text-sm"
                  onClick={() => toggleItem(item)}
                >
                  Uncheck
                </button>
              </div>
            ))}
            {checkedItems.length === 0 && (
              <p className="text-sm text-slate-500">No items checked yet.</p>
            )}
          </div>
        </div>

        <div className="mt-6 flex items-center justify-between">
          <p className="text-sm text-slate-500">
            Uncheck sequence tracked: {uncheckSequence.length} item(s)
          </p>
          <button
            className="rounded-lg bg-slate-900 px-4 py-2 text-white disabled:opacity-50"
            onClick={saveLearnedOrder}
            disabled={!shopId || uncheckSequence.length === 0}
          >
            Save learned order
          </button>
        </div>
      </div>

      <div className="rounded-2xl bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold">Add custom item</h3>
        <form onSubmit={addCustomItem} className="mt-4 grid gap-3 md:grid-cols-4">
          <input
            className="rounded-lg border border-slate-200 px-3 py-2"
            placeholder="Name"
            value={customName}
            onChange={(event) => setCustomName(event.target.value)}
          />
          <input
            className="rounded-lg border border-slate-200 px-3 py-2"
            placeholder="Category"
            value={customCategory}
            onChange={(event) => setCustomCategory(event.target.value)}
          />
          <input
            className="rounded-lg border border-slate-200 px-3 py-2"
            placeholder="Quantity"
            value={customQuantity}
            onChange={(event) => setCustomQuantity(event.target.value)}
          />
          <input
            className="rounded-lg border border-slate-200 px-3 py-2"
            placeholder="Unit"
            value={customUnit}
            onChange={(event) => setCustomUnit(event.target.value)}
          />
          <button className="rounded-lg bg-slate-900 px-4 py-2 text-white" type="submit">
            Add item
          </button>
        </form>
      </div>
    </div>
  );
}
