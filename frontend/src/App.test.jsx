import React from "react";
import { beforeEach, afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App";
import * as api from "./api";

vi.mock("./api", () => ({
  listNotes: vi.fn(),
  createNote: vi.fn(),
  updateNote: vi.fn(),
  deleteNote: vi.fn(),
}));

describe("App", () => {
  beforeEach(() => {
    vi.mocked(api.listNotes).mockResolvedValue([]);
    vi.mocked(api.createNote).mockResolvedValue({
      id: 1,
      title: "First note",
      body: "Body",
      created_at: "2026-05-20T00:00:00Z",
      updated_at: "2026-05-20T00:00:00Z",
    });
    vi.mocked(api.updateNote).mockResolvedValue({
      id: 1,
      title: "Updated note",
      body: "Updated body",
      created_at: "2026-05-20T00:00:00Z",
      updated_at: "2026-05-20T00:00:00Z",
    });
    vi.mocked(api.deleteNote).mockResolvedValue(undefined);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders the empty state and creates a note", async () => {
    const user = userEvent.setup();
    render(<App />);

    expect(await screen.findByText("No notes yet. Create the first one above.")).toBeInTheDocument();

    await user.type(screen.getByLabelText("Title"), "First note");
    await user.type(screen.getByLabelText("Body"), "Body");
    await user.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() => expect(api.createNote).toHaveBeenCalledWith({ title: "First note", body: "Body" }));
    expect(await screen.findByText("Note created.")).toBeInTheDocument();
    expect(screen.getByText("First note")).toBeInTheDocument();
  });

  it("edits and deletes notes from the list", async () => {
    vi.mocked(api.listNotes).mockResolvedValueOnce([
      {
        id: 1,
        title: "Seed note",
        body: "Seed body",
        created_at: "2026-05-20T00:00:00Z",
        updated_at: "2026-05-20T00:00:00Z",
      },
    ]);

    const user = userEvent.setup();
    render(<App />);

    expect(await screen.findByText("Seed note")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Edit" }));

    expect(screen.getByLabelText("Title")).toHaveValue("Seed note");
    await user.clear(screen.getByLabelText("Title"));
    await user.type(screen.getByLabelText("Title"), "Updated note");
    await user.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() => expect(api.updateNote).toHaveBeenCalledWith(1, { title: "Updated note", body: "Seed body" }));
    expect(await screen.findByText("Note updated.")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Delete" }));
    await waitFor(() => expect(api.deleteNote).toHaveBeenCalledWith(1));
    expect(await screen.findByText("Note deleted.")).toBeInTheDocument();
  });
});
