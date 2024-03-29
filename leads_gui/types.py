from tkinter import Widget as _Widget

from customtkinter import CTkBaseClass as _CTkBaseClass

type Widget = _Widget | _CTkBaseClass
type Font = tuple[str, int]
type Color = str | tuple[str, str]
