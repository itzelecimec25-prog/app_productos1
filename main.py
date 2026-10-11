import flet as ft  # type: ignore
from control.app import AppController

# La función recibe la ventana/página activa y
# decide si debe mostrar la pantalla de Login o el Catálogo de productos
def main(page: ft.Page):
    controller = AppController(page)
    controller.start()

# Inicia la aplicación Flet
ft.run(main)