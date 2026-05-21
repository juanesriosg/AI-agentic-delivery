import React, { useEffect, useState } from "react";
import { createNote, deleteNote, listNotes, updateNote } from "./api";

const EMPTY_FORM = { title: "", body: "" };

export default function App() {
  const [notes, setNotes] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const items = await listNotes();
        if (!cancelled) setNotes(items);
      } catch (err) {
        if (!cancelled) setError(err.message || "Failed to load notes");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  function beginEdit(note) {
    setEditingId(note.id);
    setForm({ title: note.title, body: note.body ?? "" });
    setMessage("");
    setError("");
  }

  function cancelEdit() {
    setEditingId(null);
    setForm(EMPTY_FORM);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");
    try {
      const payload = {
        title: form.title,
        body: form.body,
      };
      const saved = editingId === null
        ? await createNote(payload)
        : await updateNote(editingId, payload);
      setNotes((current) => {
        if (editingId === null) {
          return [...current, saved];
        }
        return current.map((note) => (note.id === saved.id ? saved : note));
      });
      setForm(EMPTY_FORM);
      setEditingId(null);
      setMessage(editingId === null ? "Note created." : "Note updated.");
    } catch (err) {
      setError(err.message || "Unable to save note");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id) {
    setSaving(true);
    setError("");
    setMessage("");
    try {
      await deleteNote(id);
      setNotes((current) => current.filter((note) => note.id !== id));
      if (editingId === id) {
        cancelEdit();
      }
      setMessage("Note deleted.");
    } catch (err) {
      setError(err.message || "Unable to delete note");
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="shell" aria-busy={loading || saving}>
      <section className="hero">
        <div>
          <p className="eyebrow">Pipeline smoke</p>
          <h1>Notes CRUD</h1>
          <p className="lede">
            A tiny local CRUD surface that exercises the real notes API and exposes
            the states the pipeline needs to verify.
          </p>
        </div>
        <div className="status-card" aria-live="polite">
          <strong>{loading ? "Loading notes" : `${notes.length} note(s)`}</strong>
          <span>{saving ? "Saving changes" : "Ready"}</span>
        </div>
      </section>

      <section className="panel">
        <h2>{editingId === null ? "New note" : "Edit note"}</h2>
        <form onSubmit={handleSubmit} className="note-form">
          <p className="form-help" id="note-form-help">
            Title is required. Body is optional.
          </p>
          <label>
            <span>
              Title <span className="required-indicator">(required)</span>
            </span>
            <input
              aria-label="Title"
              aria-describedby="note-form-help"
              value={form.title}
              onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
              required
            />
          </label>
          <label>
            <span>
              Body <span className="optional-indicator">(optional)</span>
            </span>
            <textarea
              aria-label="Body"
              aria-describedby="note-form-help"
              rows={5}
              value={form.body}
              onChange={(event) => setForm((current) => ({ ...current, body: event.target.value }))}
            />
          </label>
          <div className="actions">
            <button type="submit" disabled={saving}>
              Save
            </button>
            {editingId !== null ? (
              <button type="button" className="secondary" onClick={cancelEdit} disabled={saving}>
                Cancel
              </button>
            ) : null}
          </div>
        </form>
        {error ? <p className="feedback error" role="alert">{error}</p> : null}
        {message ? <p className="feedback success" role="status">{message}</p> : null}
      </section>

      <section className="panel">
        <h2>Notes</h2>
        {loading ? (
          <p>Loading notes...</p>
        ) : notes.length === 0 ? (
          <p className="empty">No notes yet. Create the first one above.</p>
        ) : (
          <ul className="notes-list">
            {notes.map((note) => (
              <li key={note.id} className="note-card">
                <div>
                  <h3>{note.title}</h3>
                  <p>{note.body || "No body provided."}</p>
                </div>
                <div className="row-actions">
                  <button type="button" onClick={() => beginEdit(note)} disabled={saving}>
                    Edit
                  </button>
                  <button type="button" className="danger" onClick={() => handleDelete(note.id)} disabled={saving}>
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
