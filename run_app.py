"""Main UI Launcher for Cadence (chinni-app).

Sets up the CustomTkinter root application, manages global app state,
provides the persistent navigation bar, and switches between screens.
"""

import sys
import customtkinter as ctk
from ui import api_client
from ui.home_screen import HomeScreen
from ui.tests_screen import TestsScreen
from ui.trends_screen import TrendsScreen
from ui.focus_timer import FocusTimerScreen

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class CadenceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Cadence (chinni-app) — Study Rhythm & Multi-Subject Tracker")
        self.geometry("1120x760")
        self.minsize(980, 680)

        # Shared application state across screens
        self.app_state = {
            "students": [],
            "current_student": None,
            "tracks": [],
            "current_track": None,
        }

        self._build_sidebar()
        self._build_main_container()
        self._check_backend_status()
        self.navigate("home")

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=("#F1F5F9", "#0F172A"))
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Brand
        brand_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_box.pack(fill="x", padx=20, pady=(25, 20))

        ctk.CTkLabel(
            brand_box,
            text="⚡ CADENCE",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#0284C7", "#38BDF8"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            brand_box,
            text="chinni-app v1.0",
            font=ctk.CTkFont(size=11),
            text_color=("#64748B", "#94A3B8"),
        ).pack(anchor="w")

        # Nav Buttons
        nav_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_box.pack(fill="x", padx=12, pady=10)

        self.nav_buttons = {}

        items = [
            ("home", "📊 Dashboard"),
            ("tests", "📝 Log a Test"),
            ("trends", "📈 Trends & Ranking"),
            ("timer", "⏱️ Focus Timer"),
        ]

        for screen_key, label in items:
            btn = ctk.CTkButton(
                nav_box,
                text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w",
                height=42,
                corner_radius=8,
                fg_color="transparent",
                text_color=("#334155", "#E2E8F0"),
                hover_color=("#E2E8F0", "#1E293B"),
                command=lambda k=screen_key: self.navigate(k),
            )
            btn.pack(fill="x", pady=4)
            self.nav_buttons[screen_key] = btn

        # Backend Health Status Badge at bottom
        status_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        status_box.pack(side="bottom", fill="x", padx=16, pady=20)

        self.health_badge = ctk.CTkLabel(
            status_box,
            text="● Checking Server...",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#E2E8F0", "#1E293B"),
            text_color="#94A3B8",
            corner_radius=6,
            padx=10,
            pady=6,
        )
        self.health_badge.pack(fill="x")

        retry_btn = ctk.CTkButton(
            status_box,
            text="🔄 Reconnect API",
            font=ctk.CTkFont(size=11),
            height=26,
            fg_color="#334155",
            hover_color="#475569",
            command=self._check_backend_status,
        )
        retry_btn.pack(fill="x", pady=(6, 0))

    def _build_main_container(self):
        self.main_container = ctk.CTkFrame(self, fg_color=("#F8FAFC", "#0B0F19"))
        self.main_container.pack(side="right", fill="both", expand=True)

        # Instantiate screens
        self.screens = {
            "home": HomeScreen(self.main_container, self.app_state, self.navigate),
            "tests": TestsScreen(self.main_container, self.app_state, self.navigate),
            "trends": TrendsScreen(self.main_container, self.app_state, self.navigate),
            "timer": FocusTimerScreen(self.main_container, self.app_state, self.navigate),
        }

    def navigate(self, screen_key: str):
        # Update active button visual
        for k, btn in self.nav_buttons.items():
            if k == screen_key:
                btn.configure(fg_color=("#0284C7", "#0284C7"), text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", text_color=("#334155", "#E2E8F0"))

        # Switch visible screen
        for k, screen in self.screens.items():
            if k == screen_key:
                screen.pack(fill="both", expand=True)
                # Refresh data when switching to screen
                if hasattr(screen, "refresh_data"):
                    screen.refresh_data()
                elif hasattr(screen, "refresh_form"):
                    screen.refresh_form()
                elif hasattr(screen, "refresh_trends"):
                    screen.refresh_trends()
                elif hasattr(screen, "refresh_timer_screen"):
                    screen.refresh_timer_screen()
            else:
                screen.pack_forget()

    def _check_backend_status(self):
        healthy = api_client.check_backend_health()
        if healthy:
            self.health_badge.configure(
                text="● API Connected (8000)",
                fg_color=("#D1FAE5", "#064E3B"),
                text_color=("#047857", "#6EE7B7"),
            )
        else:
            self.health_badge.configure(
                text="▲ Server Disconnected",
                fg_color=("#FEE2E2", "#7F1D1D"),
                text_color=("#B91C1C", "#FCA5A5"),
            )


if __name__ == "__main__":
    app = CadenceApp()
    app.mainloop()
