"""Login & Sign Up popup window for Cadence (chinni-app).

Integrates teammate's LoginPage design with backend authentication
(/auth/login and /auth/signup), supporting regular users and admin.
"""

import customtkinter as ctk
from ui import api_client

BG_COLOR = "#0b132b"
CARD_BG = "#1c2541"
TEXT_COLOR = "#ffffff"
ACCENT_COLOR = "#3a86ff"


class LoginPage(ctk.CTkToplevel):
    def __init__(self, parent, on_success_callback, on_close_callback=None):
        super().__init__(parent)
        self.title("Cadence - Login")
        self.geometry("450x470")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)
        self.on_success_callback = on_success_callback
        self.on_close_callback = on_close_callback
        self._mode = "login"  # "login" or "signup"

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.card = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=12)
        self.card.pack(fill="both", expand=True, padx=25, pady=25)

        ctk.CTkLabel(
            self.card,
            text="CADENCE",
            font=ctk.CTkFont(family="Arial", size=22, weight="bold"),
            text_color=ACCENT_COLOR,
        ).pack(pady=(24, 4))

        ctk.CTkLabel(
            self.card,
            text="Study Rhythm & Multi-Subject Tracker",
            font=ctk.CTkFont(family="Arial", size=11),
            text_color="#8d99ae",
        ).pack(pady=(0, 14))

        self.mode_label = ctk.CTkLabel(
            self.card,
            text="Log In to Your Account",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            text_color=TEXT_COLOR,
        )
        self.mode_label.pack(pady=(0, 12))

        self.username_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="Username",
            width=280,
            height=40,
            fg_color=BG_COLOR,
            border_color=ACCENT_COLOR,
            text_color=TEXT_COLOR,
        )
        self.username_entry.pack(pady=8)

        self.password_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="Password",
            show="*",
            width=280,
            height=40,
            fg_color=BG_COLOR,
            border_color=ACCENT_COLOR,
            text_color=TEXT_COLOR,
        )
        self.password_entry.pack(pady=8)
        self.password_entry.bind("<Return>", lambda e: self.handle_submit())

        self.status_label = ctk.CTkLabel(
            self.card,
            text="",
            font=ctk.CTkFont(family="Arial", size=11, weight="bold"),
            text_color="#ff6b6b",
        )
        self.status_label.pack(pady=(4, 4))

        self.submit_btn = ctk.CTkButton(
            self.card,
            text="Login",
            command=self.handle_submit,
            width=280,
            height=40,
            fg_color=ACCENT_COLOR,
            hover_color="#2667cc",
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
        )
        self.submit_btn.pack(pady=(8, 10))

        self.toggle_btn = ctk.CTkButton(
            self.card,
            text="Don't have an account? Sign Up",
            command=self._toggle_mode,
            width=280,
            height=28,
            fg_color="transparent",
            hover_color="#253256",
            text_color="#8ecae6",
            font=ctk.CTkFont(family="Arial", size=11),
        )
        self.toggle_btn.pack(pady=(0, 8))

        ctk.CTkLabel(
            self.card,
            text="Admin login: admin / admin123",
            font=ctk.CTkFont(family="Arial", size=10),
            text_color="#6c7a96",
        ).pack(pady=(2, 12))

    def _toggle_mode(self):
        if self._mode == "login":
            self._mode = "signup"
            self.title("Cadence - Sign Up")
            self.mode_label.configure(text="Create a New Account")
            self.submit_btn.configure(text="Sign Up")
            self.toggle_btn.configure(text="Already have an account? Log In")
        else:
            self._mode = "login"
            self.title("Cadence - Login")
            self.mode_label.configure(text="Log In to Your Account")
            self.submit_btn.configure(text="Login")
            self.toggle_btn.configure(text="Don't have an account? Sign Up")
        self.status_label.configure(text="")

    def _on_close(self):
        self.destroy()
        if self.on_close_callback:
            self.on_close_callback()

    def handle_submit(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.status_label.configure(text="Please fill in all fields.", text_color="#ff6b6b")
            return

        if self._mode == "signup" and len(password) < 4:
            self.status_label.configure(text="Password must be at least 4 characters.", text_color="#ff6b6b")
            return

        try:
            if self._mode == "login":
                user = api_client.login(username, password)
            else:
                user = api_client.signup(username, password)

            self.destroy()
            self.on_success_callback(user)
        except Exception as e:
            err = str(e)
            if "401" in err:
                self.status_label.configure(text="Invalid username or password.", text_color="#ff6b6b")
            elif "409" in err:
                self.status_label.configure(text="Username is already taken.", text_color="#ff6b6b")
            elif "Connection" in err or "connect" in err.lower():
                self.status_label.configure(text="Cannot reach backend. Run run_backend.py first.", text_color="#ff6b6b")
            else:
                self.status_label.configure(text=f"Auth error: {err[:55]}", text_color="#ff6b6b")
