import { render, screen } from "@testing-library/react";
import { App } from "./App";
it("mostra o título", () => {
  render(<App />);
  expect(screen.getByRole("heading", { level: 1 })).toBeTruthy();
});
