const DEFAULT_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

async function parseResponse(response) {
  const text = await response.text();
  let payload = null;
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = { error: text };
    }
  }
  if (!response.ok) {
    const error = new Error(payload?.error || "Request failed");
    error.status = response.status;
    throw error;
  }
  return payload;
}

async function request(path, options = {}) {
  const response = await fetch(`${DEFAULT_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });
  return parseResponse(response);
}

export async function listNotes() {
  const data = await request("/api/notes");
  return data.notes ?? [];
}

export async function createNote(note) {
  return request("/api/notes", {
    method: "POST",
    body: JSON.stringify(note),
  });
}

export async function updateNote(id, note) {
  return request(`/api/notes/${id}`, {
    method: "PUT",
    body: JSON.stringify(note),
  });
}

export async function deleteNote(id) {
  await request(`/api/notes/${id}`, {
    method: "DELETE",
  });
}
