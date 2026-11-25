"""Login & Sign Up screen for Cadence (chinni-app).

Integrates teammate's LoginPage design with backend authentication
(/auth/login and /auth/signup), supporting regular users, admin, and
track/class selection when signing up.
"""

import customtkinter as ctk
from ui import api_client

BG_COLOR = "#0b132b"
CARD_BG = "#1c2541"
TEXT_COLOR = "#ffffff"
ACCENT_COLOR = "#3a86ff"


class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, on_success_callback):
        super().__init__(parent, fg_color=BG_COLOR)
        self.on_success_callback = on_success_callback
        self._mode = "login"  # "login" or "signup"

        self.card = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=12)
        self.card.pack(fill="both", expand=True, padx=25, pady=25)

        ctk.CTkLabel(
            self.card,
            text="CADENCE",
            font=ctk.CTkFont(family="Arial", size=22, weight="bold"),
            text_color=ACCENT_COLOR,
        ).pack(pady=(22, 4))

        ctk.CTkLabel(
            self.card,
            text="Study Rhythm & Multi-Subject Tracker",
            font=ctk.CTkFont(family="Arial", size=11),
            text_color="#8d99ae",
        ).pack(pady=(0, 12))

        self.mode_label = ctk.CTkLabel(
            self.card,
            text="Log In to Your Account",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            text_color=TEXT_COLOR,
        )
        self.mode_label.pack(pady=(0, 10))

        self.username_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="Username",
            width=280,
            height=38,
            fg_color=BG_COLOR,
            border_color=ACCENT_COLOR,
            text_color=TEXT_COLOR,
        )
        self.username_entry.pack(pady=6)

        self.password_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="Password",
            show="*",
            width=280,
            height=38,
            fg_color=BG_COLOR,
            border_color=ACCENT_COLOR,
            text_color=TEXT_COLOR,
        )
        self.password_entry.pack(pady=6)
        self.password_entry.bind("<Return>", lambda e: self.handle_submit())

        # Starting track selector (shown only during Sign Up)
        self.track_picker_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        ctk.CTkLabel(
            self.track_picker_frame,
            text="Starting Track / Class:",
            font=ctk.CTkFont(family="Arial", size=11, weight="bold"),
            text_color="#cbd5e1",
        ).pack(anchor="w")
        self.track_template_var = ctk.StringVar(value="JEE Main 2026")
        self.track_menu = ctk.CTkOptionMenu(
            self.track_picker_frame,
            variable=self.track_template_var,
            values=["JEE Main 2026", "CBSE 8th Grade", "CBSE 12th Board"],
            width=280,
            height=34,
            fg_color=BG_COLOR,
            button_color=ACCENT_COLOR,
        )
        self.track_menu.pack(pady=(4, 0))

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
        self.submit_btn.pack(pady=(6, 8))

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
        self.toggle_btn.pack(pady=(0, 6))

        ctk.CTkLabel(
            self.card,
            text="Admin login: admin / admin123",
            font=ctk.CTkFont(family="Arial", size=10),
            text_color="#6c7a96",
        ).pack(pady=(2, 10))

    def _toggle_mode(self):
        if self._mode == "login":
            self._mode = "signup"
            self.mode_label.configure(text="Create a New Account")
            self.submit_btn.configure(text="Sign Up")
            self.toggle_btn.configure(text="Already have an account? Log In")
            self.track_picker_frame.pack(before=self.status_label, pady=(4, 4))
            try:
                self.winfo_toplevel().geometry("450x540")
            except Exception:
                pass
        else:
            self._mode = "login"
            self.mode_label.configure(text="Log In to Your Account")
            self.submit_btn.configure(text="Login")
            self.toggle_btn.configure(text="Don't have an account? Sign Up")
            self.track_picker_frame.pack_forget()
            try:
                self.winfo_toplevel().geometry("450x470")
            except Exception:
                pass
        self.status_label.configure(text="")

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
                user = api_client.signup(
                    username,
                    password,
                    track_template=self.track_template_var.get(),
                )

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
