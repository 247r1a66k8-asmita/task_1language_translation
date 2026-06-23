"""
CodeAlpha Internship - Task 1: Language Translation Tool
=========================================================
A GUI-based Language Translation Tool using Google Translate API (via deep-translator).
Features:
  - Select source and target languages from dropdowns
  - Translate text with one click
  - Copy translated text to clipboard
  - Text-to-speech for translated output
  - Swap languages button
  - Character counter

Requirements:
    pip install deep-translator tkinter pyttsx3 pyperclip
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

# ── Third-party (install once) ──────────────────────────────────────────────
try:
    from deep_translator import GoogleTranslator
except ImportError:
    raise SystemExit(
        "Missing library: run  pip install deep-translator  then try again."
    )

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import pyperclip
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False

# ── Language map (display name → ISO code) ──────────────────────────────────
LANGUAGES = {
    "Auto Detect":  "auto",
    "Afrikaans":    "af",
    "Albanian":     "sq",
    "Arabic":       "ar",
    "Bengali":      "bn",
    "Bulgarian":    "bg",
    "Chinese (Simplified)":  "zh-CN",
    "Chinese (Traditional)": "zh-TW",
    "Croatian":     "hr",
    "Czech":        "cs",
    "Danish":       "da",
    "Dutch":        "nl",
    "English":      "en",
    "Finnish":      "fi",
    "French":       "fr",
    "German":       "de",
    "Greek":        "el",
    "Gujarati":     "gu",
    "Hebrew":       "iw",
    "Hindi":        "hi",
    "Hungarian":    "hu",
    "Indonesian":   "id",
    "Italian":      "it",
    "Japanese":     "ja",
    "Kannada":      "kn",
    "Korean":       "ko",
    "Malay":        "ms",
    "Malayalam":    "ml",
    "Marathi":      "mr",
    "Nepali":       "ne",
    "Norwegian":    "no",
    "Pashto":       "ps",
    "Persian":      "fa",
    "Polish":       "pl",
    "Portuguese":   "pt",
    "Punjabi":      "pa",
    "Romanian":     "ro",
    "Russian":      "ru",
    "Serbian":      "sr",
    "Sinhala":      "si",
    "Slovak":       "sk",
    "Slovenian":    "sl",
    "Spanish":      "es",
    "Swahili":      "sw",
    "Swedish":      "sv",
    "Tamil":        "ta",
    "Telugu":       "te",
    "Thai":         "th",
    "Turkish":      "tr",
    "Ukrainian":    "uk",
    "Urdu":         "ur",
    "Vietnamese":   "vi",
    "Welsh":        "cy",
}

LANG_NAMES = list(LANGUAGES.keys())


# ── Main App ─────────────────────────────────────────────────────────────────
class TranslationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌐 Language Translator — CodeAlpha Task 1")
        self.geometry("900x600")
        self.resizable(True, True)
        self.configure(bg="#1e1e2e")
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Palette ──────────────────────────────────────────────────────────
        BG      = "#1e1e2e"
        PANEL   = "#2a2a3e"
        ACCENT  = "#7c6af7"
        TEXT    = "#cdd6f4"
        MUTED   = "#6c7086"
        BTN_FG  = "#ffffff"

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox",
                        fieldbackground=PANEL, background=PANEL,
                        foreground=TEXT, selectbackground=ACCENT,
                        arrowcolor=TEXT, borderwidth=0)
        style.map("TCombobox", fieldbackground=[("readonly", PANEL)])

        # ── Title bar ────────────────────────────────────────────────────────
        title_bar = tk.Frame(self, bg=PANEL, pady=10)
        title_bar.pack(fill="x")
        tk.Label(title_bar, text="🌐  Language Translator",
                 font=("Segoe UI", 18, "bold"),
                 fg=ACCENT, bg=PANEL).pack()
        tk.Label(title_bar, text="Powered by Google Translate  •  CodeAlpha Internship",
                 font=("Segoe UI", 9), fg=MUTED, bg=PANEL).pack()

        # ── Language selector row ─────────────────────────────────────────────
        sel_row = tk.Frame(self, bg=BG, pady=12)
        sel_row.pack(fill="x", padx=30)

        # Source language
        src_frame = tk.Frame(sel_row, bg=BG)
        src_frame.pack(side="left", expand=True, fill="x")
        tk.Label(src_frame, text="Source Language", font=("Segoe UI", 10),
                 fg=MUTED, bg=BG).pack(anchor="w")
        self.src_var = tk.StringVar(value="Auto Detect")
        src_cb = ttk.Combobox(src_frame, textvariable=self.src_var,
                              values=LANG_NAMES, state="readonly", width=25)
        src_cb.pack(fill="x", pady=3)

        # Swap button
        swap_frame = tk.Frame(sel_row, bg=BG, padx=15)
        swap_frame.pack(side="left")
        tk.Button(swap_frame, text="⇄", font=("Segoe UI", 16),
                  bg=ACCENT, fg=BTN_FG, relief="flat", cursor="hand2",
                  command=self._swap_languages,
                  padx=10, pady=4).pack(pady=20)

        # Target language
        tgt_frame = tk.Frame(sel_row, bg=BG)
        tgt_frame.pack(side="left", expand=True, fill="x")
        tk.Label(tgt_frame, text="Target Language", font=("Segoe UI", 10),
                 fg=MUTED, bg=BG).pack(anchor="w")
        self.tgt_var = tk.StringVar(value="Hindi")
        tgt_cb = ttk.Combobox(tgt_frame, textvariable=self.tgt_var,
                              values=LANG_NAMES[1:], state="readonly", width=25)
        tgt_cb.pack(fill="x", pady=3)

        # ── Text panels ──────────────────────────────────────────────────────
        panels = tk.Frame(self, bg=BG)
        panels.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        # Input
        in_frame = tk.Frame(panels, bg=PANEL, bd=0)
        in_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

        in_header = tk.Frame(in_frame, bg=PANEL)
        in_header.pack(fill="x", padx=8, pady=(6, 0))
        tk.Label(in_header, text="Enter Text", font=("Segoe UI", 10, "bold"),
                 fg=TEXT, bg=PANEL).pack(side="left")
        self.char_lbl = tk.Label(in_header, text="0 / 5000",
                                 font=("Segoe UI", 9), fg=MUTED, bg=PANEL)
        self.char_lbl.pack(side="right")

        self.input_text = scrolledtext.ScrolledText(
            in_frame, font=("Segoe UI", 11), bg="#1a1a2e", fg=TEXT,
            insertbackground=TEXT, relief="flat", wrap="word",
            padx=10, pady=8, height=12)
        self.input_text.pack(fill="both", expand=True, padx=6, pady=6)
        self.input_text.bind("<KeyRelease>", self._update_char_count)

        tk.Button(in_frame, text="✖  Clear", font=("Segoe UI", 9),
                  bg="#3a3a4e", fg=MUTED, relief="flat", cursor="hand2",
                  command=self._clear_input).pack(anchor="e", padx=8, pady=(0, 6))

        # Output
        out_frame = tk.Frame(panels, bg=PANEL, bd=0)
        out_frame.pack(side="left", fill="both", expand=True, padx=(8, 0))

        out_header = tk.Frame(out_frame, bg=PANEL)
        out_header.pack(fill="x", padx=8, pady=(6, 0))
        tk.Label(out_header, text="Translation", font=("Segoe UI", 10, "bold"),
                 fg=TEXT, bg=PANEL).pack(side="left")

        self.output_text = scrolledtext.ScrolledText(
            out_frame, font=("Segoe UI", 11), bg="#1a1a2e", fg="#a6e3a1",
            relief="flat", wrap="word", padx=10, pady=8,
            height=12, state="disabled")
        self.output_text.pack(fill="both", expand=True, padx=6, pady=6)

        # Output action buttons
        btn_row = tk.Frame(out_frame, bg=PANEL)
        btn_row.pack(anchor="e", padx=8, pady=(0, 6))
        tk.Button(btn_row, text="📋 Copy", font=("Segoe UI", 9),
                  bg="#3a3a4e", fg=TEXT, relief="flat", cursor="hand2",
                  command=self._copy_translation).pack(side="left", padx=2)
        if TTS_AVAILABLE:
            tk.Button(btn_row, text="🔊 Speak", font=("Segoe UI", 9),
                      bg="#3a3a4e", fg=TEXT, relief="flat", cursor="hand2",
                      command=self._speak_translation).pack(side="left", padx=2)

        # ── Translate button ──────────────────────────────────────────────────
        self.translate_btn = tk.Button(
            self, text="Translate  →", font=("Segoe UI", 13, "bold"),
            bg=ACCENT, fg=BTN_FG, relief="flat", cursor="hand2",
            padx=30, pady=10, command=self._translate_threaded)
        self.translate_btn.pack(pady=(0, 10))

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self, textvariable=self.status_var,
                 font=("Segoe UI", 9), fg=MUTED, bg="#1e1e2e").pack(pady=(0, 6))

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _update_char_count(self, _event=None):
        n = len(self.input_text.get("1.0", "end-1c"))
        self.char_lbl.config(text=f"{n} / 5000")

    def _clear_input(self):
        self.input_text.delete("1.0", "end")
        self._update_char_count()

    def _swap_languages(self):
        src = self.src_var.get()
        tgt = self.tgt_var.get()
        if src == "Auto Detect":
            messagebox.showinfo("Swap", "Cannot swap when source is 'Auto Detect'.")
            return
        self.src_var.set(tgt)
        self.tgt_var.set(src)

    def _set_output(self, text: str):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", text)
        self.output_text.config(state="disabled")

    def _copy_translation(self):
        result = self.output_text.get("1.0", "end-1c").strip()
        if not result:
            messagebox.showinfo("Copy", "Nothing to copy yet.")
            return
        if CLIP_AVAILABLE:
            pyperclip.copy(result)
            self.status_var.set("✅ Copied to clipboard!")
        else:
            self.clipboard_clear()
            self.clipboard_append(result)
            self.status_var.set("✅ Copied to clipboard (fallback)!")

    def _speak_translation(self):
        text = self.output_text.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showinfo("Speak", "Nothing to speak yet.")
            return

        def _tts():
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", 160)
                engine.say(text)
                engine.runAndWait()
            except Exception as exc:
                messagebox.showerror("TTS Error", str(exc))

        threading.Thread(target=_tts, daemon=True).start()

    # ── Core translation ──────────────────────────────────────────────────────
    def _translate_threaded(self):
        """Run translation in a background thread so the UI stays responsive."""
        src_text = self.input_text.get("1.0", "end-1c").strip()
        if not src_text:
            messagebox.showwarning("Input Required", "Please enter text to translate.")
            return

        src_code = LANGUAGES[self.src_var.get()]
        tgt_code = LANGUAGES.get(self.tgt_var.get())
        if not tgt_code or tgt_code == "auto":
            messagebox.showwarning("Target Language", "Please select a valid target language.")
            return

        self.translate_btn.config(state="disabled", text="Translating…")
        self.status_var.set("Translating…")
        threading.Thread(target=self._do_translate,
                         args=(src_text, src_code, tgt_code),
                         daemon=True).start()

    def _do_translate(self, text: str, src: str, tgt: str):
        try:
            translator = GoogleTranslator(source=src, target=tgt)
            result = translator.translate(text)
            self.after(0, self._on_translation_done, result, None)
        except Exception as exc:
            self.after(0, self._on_translation_done, None, str(exc))

    def _on_translation_done(self, result, error):
        self.translate_btn.config(state="normal", text="Translate  →")
        if error:
            self.status_var.set(f"❌ Error: {error}")
            messagebox.showerror("Translation Error", error)
        else:
            self._set_output(result)
            self.status_var.set("✅ Translation complete!")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = TranslationApp()
    app.mainloop()
