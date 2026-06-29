import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { authService } from "@/lib/auth/AuthService";
import { renderWithProviders } from "@/test/utils";

import { LoginScreen } from "./LoginScreen";

describe("LoginScreen", () => {
  it("validates the email before submitting", async () => {
    renderWithProviders(<LoginScreen />);
    await userEvent.type(screen.getByLabelText("Email"), "not-an-email");
    await userEvent.type(screen.getByLabelText("Password"), "secret");
    await userEvent.click(screen.getByRole("button", { name: /^log in$/i }));

    expect(await screen.findByText(/valid email/i)).toBeInTheDocument();
    expect(authService.signInWithPassword).not.toHaveBeenCalled();
  });

  it("signs in with the entered credentials", async () => {
    renderWithProviders(<LoginScreen />);
    await userEvent.type(screen.getByLabelText("Email"), "user@example.com");
    await userEvent.type(screen.getByLabelText("Password"), "supersecret");
    await userEvent.click(screen.getByRole("button", { name: /^log in$/i }));

    await waitFor(() =>
      expect(authService.signInWithPassword).toHaveBeenCalledWith(
        "user@example.com",
        "supersecret",
      ),
    );
  });

  it("offers a one-click demo sign-in", async () => {
    renderWithProviders(<LoginScreen />);
    await userEvent.click(screen.getByRole("button", { name: /try the demo/i }));
    await waitFor(() => expect(authService.signInWithDemo).toHaveBeenCalled());
  });

  it("toggles password visibility", async () => {
    renderWithProviders(<LoginScreen />);
    const password = screen.getByLabelText("Password") as HTMLInputElement;
    expect(password.type).toBe("password");
    await userEvent.click(screen.getByRole("button", { name: /show password/i }));
    expect(password.type).toBe("text");
  });
});
