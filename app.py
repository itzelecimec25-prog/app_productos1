# Importa el módulo de la librería Flet para gestionar la interfaz gráfica
import flet as ft  # type: ignore
from servicios.sesion import SessionService
from servicios.api import ApiService

# Define la clase principal que coordina las vistas de la app
class AppController:
    # Constructor de la clase que recibe el objeto página principal de Flet
    def __init__(self, page: ft.Page):
        # Guarda la referencia a la página
        self.page = page
        # Instancia para gestionar la sesión del usuario
        self.session = SessionService()
        # Aplicar la configuración básica de la ventana
        self._configure_page()

    # Método para configurar la alineación y el título de la página
    def _configure_page(self):
        # Establece el título 
        self.page.title = "App FakeStore"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        # Centra los elementos horizontalmente
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Método para iniciar el flujo de la aplicación según el estado de la sesión
    def start(self):
        # Evalúa si el usuario ya cuenta con una sesión iniciada
        if self.session.esta_autenticado():
            # Carga la vista del catálogo de productos si está autenticado
            self.load_catalog()
        # Si no hay una sesión activa
        else:
            # Manda de nuevo el formulario de inicio de sesión
            self.build_login_ui()

    # Método para cerrar la sesión actual y regresar al inicio de sesión
    def logout(self, e=None):
        # Restablece y limpia los datos de la sesión del usuario, elimina los elementos de la interfaz y 
        # carga el formulario de login
        self.session.cerrar_sesion()
        self.page.clean()
        self.build_login_ui()

    # Método para procesa el intento de autenticación cuando el usuario da clic en ingresar
    def handle_login(self, username_input, password_input, error_banner):
        # Oculta el mensaje de error de la pantalla previo a procesar
        error_banner.visible = False
        # Actualiza el estado visual de la página
        self.page.update()

        # Obtiene y limpia espacios en blanco del valor del campo usuario y contraseña
        username = username_input.value.strip() if username_input.value else ""
        password = password_input.value.strip() if password_input.value else ""

        # Verifica si alguno de los dos campos se encuentra vacío
        if not username or not password:
            # Asigna un mensaje de error solicitando rellenar los datos y el segundo banner lo muestra
            error_banner.value = "Por favor, ingresa usuario y contraseña."
            error_banner.visible = True
            # Actualiza la vista para reflejar el cambio
            self.page.update()
            # Interrumpe la ejecución del método
            return

        # Bloque de captura de excepciones para peticiones a la API
        try:
            # Pide a la API realizar la autenticación con las credenciales ingresadas
            response = ApiService.login(username, password)
            # Verifica si la respuesta fue exitosa y contiene el token de acceso
            if response.status_code in [200, 201] and "token" in response.json():
                token = response.json().get("token")
                # Registra el token en el servicio de sesión
                self.session.iniciar_sesion(token)
                # Carga la vista del catálogo de productos
                self.load_catalog()
            # Si el servidor responde pero no otorga el token por credenciales inválidas
            else:
                # Define el texto de error por el servidor y visibiliza la etiqueta
                error_banner.value = f"Credenciales incorrectas (Status {response.status_code})."
                error_banner.visible = True
                # Actualiza la pantalla para mostrar el mensaje
                self.page.update()
        # Captura fallos de red u otros errores durante el proceso
        except Exception as ex:
            error_banner.value = f"Error al conectar con el servidor: {ex}"
            error_banner.visible = True
            # Actualiza los cambios en la interfaz gráfica
            self.page.update()

    # Método encargado de construir la pantalla del formulario de login
    def build_login_ui(self):
        # Remueve cualquier componente anterior presente en la página
        self.page.clean()
        # Centra verticalmente los elementos dentro de la vista
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER

        # Crea la caja de entrada de texto para el nombre de usuario
        username_input = ft.TextField(label="Usuario", width=300)
        # Crea la caja de texto para la contraseña configurada para ocultar caracteres
        password_input = ft.TextField(
            label="Contraseña", password=True, can_reveal_password=True, width=300
        )
        # Componente de texto en color rojo reservado para mensajes de error
        error_banner = ft.Text(color="red", visible=False)

        # Crea una tarjeta visual que encierra el formulario de acceso
        login_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        # Título del formulario
                        ft.Text("Iniciar Sesión", size=20, weight=ft.FontWeight.BOLD),
                        # Campo de texto para el usuario
                        username_input,
                        # Campo de texto para la contraseña 
                        password_input,
                        # Etiqueta de aviso de errores
                        error_banner,
                        # Botón que dispara la función de validación de inicio de sesión
                        ft.Button(
                            "Iniciar Sesión",
                            on_click=lambda _: self.handle_login(username_input, password_input, error_banner),
                            width=300
                        ),
                    ],
                    # Alinea y centra verticalmente los controles de la columna
                    alignment=ft.MainAxisAlignment.CENTER,
                    # Alinea y centra horizontalmente los controles de la columna
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    # Define un espaciado vertical constante de 15 px entre elementos
                    spacing=15,
                ),
                # Aplica un relleno interior de 20 px dentro del contenedor
                padding=20,
            )
        )
        # Agrega la tarjeta construida a la página principal
        self.page.add(login_card)
        # Refresca la vista de la página para mostrar los cambios
        self.page.update()

    # Método para construir y presentar la vista del catálogo de productos
    def load_catalog(self, category: str = None):
        # Limpia los componentes existentes en la ventana
        self.page.clean()
        # Establece la alineación vertical al inicio de la pantalla
        self.page.vertical_alignment = ft.MainAxisAlignment.START

        # Botón dinámico de agregar producto (Solo Administrador)
        add_product_button = []
        if self.session.user_role == "Administrador":
            add_product_button.append(
                ft.Button("Agregar Producto", icon=ft.Icons.ADD, on_click=lambda _: self.show_add_product_form())
            )

        # Construye la barra superior con el ID, rol de usuario y botón de salida
        header = ft.Row(
            controls=[
                # Muestra la información de la sesión actual
                ft.Text(f"ID: {self.session.user_id} | Rol: {self.session.user_role}", weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[
                        *add_product_button,
                        # Botón para cerrar sesión
                        ft.Button("Cerrar Sesión", on_click=self.logout, icon=ft.Icons.LOGOUT)
                    ]
                )
            ],
            # Distribuye los elementos con espacio entre ellos
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            # Fija un ancho de 800 px para la fila
            width=800
        )

        # Fila horizontal deslizable para los botones de categorías
        categories_row = ft.Row(scroll=ft.ScrollMode.ALWAYS, spacing=10)
        # Cuadrícula adaptable para renderizar las tarjetas de productos
        products_grid = ft.GridView(
            expand=True,
            max_extent=220,
            child_aspect_ratio=0.7,
            spacing=10,
            run_spacing=10
        )

        # Círculo de progreso para indicar carga de datos
        loading_spinner = ft.ProgressRing()
        # Texto para comunicar errores de carga en la vista
        error_text_ui = ft.Text("", color="red")
        # Contenedor para la sección de notificación de errores
        error_container = ft.Column(
            controls=[error_text_ui],
            visible=False,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Define la distribución vertical completa de la pantalla del catálogo
        main_layout = ft.Column(
            controls=[
                # Encabezado con datos del usuario
                header,
                # Título de la sección de categorías
                ft.Text("Categorías", weight=ft.FontWeight.BOLD),
                # Lista deslizable de categorías
                categories_row,
                # Divisor horizontal visual
                ft.Divider(),
                # Indicador de carga
                loading_spinner,
                # Mensaje/botón en caso de error
                error_container,
                # Rejilla con los productos
                products_grid
            ],
            expand=True,
            width=800,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        # Agrega la estructura principal a la página
        self.page.add(main_layout)

        # Función interna para realizar la carga asíncrona de los datos
        def fetch_data():
            # Muestra el indicador de carga en pantalla
            loading_spinner.visible = True
            # Oculta la vista de errores
            error_container.visible = False
            # Vacía los elementos previos de la cuadrícula de productos
            products_grid.controls.clear()
            # Actualiza el estado visual de la página
            self.page.update()

            try:
                # 1. Cargar categorías desde la API
                categories = ApiService.obtener_categorias()
                # Limpia la lista previa de botones de categorías
                categories_row.controls.clear()

                # Crea el botón/chip para consultar la totalidad de los productos
                all_btn = ft.Chip(
                    label=ft.Text("Ver todos"),
                    selected=(category is None),
                    on_click=lambda _: self.load_catalog(None)
                )
                # Agrega el botón "Ver todos" a la fila de categorías
                categories_row.controls.append(all_btn)

                # Iteración para agregar cada categoría devuelta por la API
                for cat in categories:
                    # Crea un componente Chip por cada categoría
                    chip = ft.Chip(
                        label=ft.Text(cat.capitalize()),
                        selected=(category == cat),
                        on_click=lambda e, c=cat: self.load_catalog(c)
                    )
                    # Agrega el chip a la fila horizontal de categorías
                    categories_row.controls.append(chip)

                # 2. Cargar productos desde la API
                products = ApiService.obtener_productos(category)
                # Recorre la lista de productos traídos de la API
                for p in products:
                    # Construye la tarjeta individual para el producto
                    card = ft.Card(
                        content=ft.Container(
                            padding=10,
                            content=ft.Column(
                                controls=[
                                    # Muestra la imagen remota del producto
                                    ft.Image(src=p.image, height=100, fit="contain"),
                                    # Título del producto con límite de 2 líneas
                                    ft.Text(p.title, max_lines=2, overflow="ellipsis", weight=ft.FontWeight.BOLD),
                                    # Muestra el precio formateado con dos decimales
                                    ft.Text(f"${p.price:.2f}", color="green", weight=ft.FontWeight.BOLD),
                                    # Botón para navegar hacia el detalle del producto
                                    ft.Button("Ver detalle", on_click=lambda _, pid=p.id: self.show_product_detail(pid))
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        )
                    )
                    # Agrega la tarjeta a la cuadrícula de productos
                    products_grid.controls.append(card)

                # Oculta el spinner tras completar la carga con éxito
                loading_spinner.visible = False
                # Refresca la interfaz de usuario con los datos cargados
                self.page.update()

            # Captura cualquier fallo generado durante la consulta a la API
            except Exception as ex:
                # Oculta el spinner de carga
                loading_spinner.visible = False
                # Escribe la descripción de la falla en el texto de error
                error_text_ui.value = f"Error al conectar con el servidor: {ex}"
                # Agrega el texto y un botón para reintentar la operación
                error_container.controls = [
                    error_text_ui,
                    ft.Button("Reintentar", on_click=lambda _: fetch_data())
                ]
                # Vuelve visible el contenedor de errores
                error_container.visible = True
                # Actualiza la vista para presentar el aviso de error
                self.page.update()

        # Dispara la ejecución de la carga de datos
        fetch_data()

    # Método para consultar y renderizar la vista detallada de un producto específico
    def show_product_detail(self, product_id: int):
        # Recupera el rol registrado del usuario actual
        role = self.session.user_role

        # Crea una vista previa simple de espera mientras se obtienen las propiedades
        loading_view = ft.Column(
            [ft.ProgressRing(), ft.Text("Cargando detalle...")],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        # Limpia la página de la pantalla actual
        self.page.clean()
        # Presenta la vista temporal de cargando
        self.page.add(loading_view)

        # Captura errores al solicitar la información
        try:
            # Obtiene el objeto con los detalles del producto desde la API
            product = ApiService.obtener_detalle_producto(product_id)

            # Lista para guardar controles condicionales según los permisos del usuario
            action_controls = []
            # US07 & US08 (Escenario 3): Solo renderiza los botones de Editar y Eliminar si el rol es Administrador
            if role == "Administrador":
                action_controls.extend([
                    ft.Button("Editar Producto", icon=ft.Icons.EDIT, on_click=lambda _: self.show_edit_product_form(product)),
                    ft.Button("Eliminar Producto", icon=ft.Icons.DELETE, on_click=lambda _: self.confirm_delete_product(product))
                ])

            # Tarjeta contenedor con el detalle explicativo del producto
            detail_card = ft.Card(
                content=ft.Container(
                    padding=20,
                    content=ft.Column(
                        controls=[
                            # Muestra la imagen completa del producto
                            ft.Image(src=product.image, width=200, height=200, fit="contain"),
                            # Título principal del producto
                            ft.Text(product.title, size=20, weight=ft.FontWeight.BOLD),
                            # Precio en formato numérico y color destacado
                            ft.Text(f"${product.price:.2f}", size=18, color="green", weight=ft.FontWeight.BOLD),
                            # Texto secundario con la categoría
                            ft.Text(f"Categoría: {product.category}", italic=True),
                            # Descripción detallada
                            ft.Text(product.description),
                            # Fila de acciones especiales de Administrador si aplican
                            ft.Row(action_controls, alignment=ft.MainAxisAlignment.CENTER) if action_controls else ft.Container(),
                            # Botón de retorno al catálogo principal
                            ft.Button("Volver al Catálogo", on_click=lambda _: self.load_catalog())
                        ],
                        spacing=15,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    )
                )
            )

            # Limpia el indicador de carga previo
            self.page.clean()
            # Despliega la tarjeta con la información detallada
            self.page.add(detail_card)

        # Captura cualquier excepción surgida al pedir los detalles
        except Exception as ex:
            # Crea un aviso emergente inferior (SnackBar) con el detalle del error
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al cargar detalle: {ex}"))
            # Activa el aviso emergente
            self.page.snack_bar.open = True
            # Regresa al usuario a la vista general del catálogo
            self.load_catalog()

    # US06: Formulario y lógica para agregar nuevo producto
    def show_add_product_form(self):
        # US06 (Escenario 3): Restricción de permisos y seguridad
        if self.session.user_role != "Administrador":
            self.page.snack_bar = ft.SnackBar(ft.Text("Acceso no autorizado. Redirigiendo al catálogo..."))
            self.page.snack_bar.open = True
            self.load_catalog()
            return

        self.page.clean()
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER

        # Controles del formulario
        title_input = ft.TextField(label="Título", width=350)
        price_input = ft.TextField(label="Precio", width=350)
        desc_input = ft.TextField(label="Descripción", multiline=True, min_lines=3, width=350)
        image_input = ft.TextField(label="URL de imagen", width=350)
        category_dropdown = ft.Dropdown(
            label="Categoría",
            width=350,
            options=[
                ft.dropdown.Option("electronics"),
                ft.dropdown.Option("jewelery"),
                ft.dropdown.Option("men's clothing"),
                ft.dropdown.Option("women's clothing")
            ]
        )

        error_banner = ft.Text("", color="red", visible=False)

        # Función para procesar el envío del formulario
        def save_product(e):
            # Restablece estilos de error (Escenario 2)
            title_input.border_color = None
            price_input.border_color = None
            desc_input.border_color = None
            image_input.border_color = None
            category_dropdown.border_color = None
            error_banner.visible = False

            has_error = False

            # Validación de campos vacíos
            if not title_input.value or not title_input.value.strip():
                title_input.border_color = "red"
                has_error = True
            if not desc_input.value or not desc_input.value.strip():
                desc_input.border_color = "red"
                has_error = True
            if not image_input.value or not image_input.value.strip():
                image_input.border_color = "red"
                has_error = True
            if not category_dropdown.value:
                category_dropdown.border_color = "red"
                has_error = True

            # Validación del precio (número válido y no vacío)
            parsed_price = None
            if not price_input.value or not price_input.value.strip():
                price_input.border_color = "red"
                has_error = True
            else:
                try:
                    parsed_price = float(price_input.value.strip())
                except ValueError:
                    price_input.border_color = "red"
                    has_error = True

            # US06 (Escenario 2): Detiene la petición de red si hay campos vacíos o incorrectos
            if has_error:
                error_banner.value = "Por favor, corrige los campos resaltados en rojo."
                error_banner.visible = True
                self.page.update()
                return

            # US06 (Escenario 1): Creación exitosa del producto
            try:
                payload = {
                    "title": title_input.value.strip(),
                    "price": parsed_price,
                    "description": desc_input.value.strip(),
                    "image": image_input.value.strip(),
                    "category": category_dropdown.value
                }
                
                response = ApiService.crear_producto(payload)

                if response.status_code in [200, 201]:
                    new_id = response.json().get("id", "N/A")
                    # Muestra alerta de confirmación con el nuevo ID
                    self.page.snack_bar = ft.SnackBar(ft.Text(f"Producto creado con éxito. ID generado: {new_id}"))
                    self.page.snack_bar.open = True
                    
                    # Limpia el formulario
                    title_input.value = ""
                    price_input.value = ""
                    desc_input.value = ""
                    image_input.value = ""
                    category_dropdown.value = None
                    self.page.update()
                else:
                    error_banner.value = f"Error al guardar en el servidor (Status {response.status_code})"
                    error_banner.visible = True
                    self.page.update()

            except Exception as ex:
                error_banner.value = f"Error de red al crear producto: {ex}"
                error_banner.visible = True
                self.page.update()

        form_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Agregar Nuevo Producto", size=20, weight=ft.FontWeight.BOLD),
                        title_input,
                        price_input,
                        desc_input,
                        image_input,
                        category_dropdown,
                        error_banner,
                        ft.Row(
                            controls=[
                                ft.Button("Guardar", on_click=save_product, icon=ft.Icons.SAVE),
                                ft.Button("Cancelar", on_click=lambda _: self.load_catalog())
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12
                ),
                padding=20
            )
        )

        self.page.add(form_card)
        self.page.update()

    # US07: Formulario y lógica para editar un producto existente
    def show_edit_product_form(self, product):
        # US07 (Escenario 3): Restricción de permisos y seguridad
        if self.session.user_role != "Administrador":
            self.page.snack_bar = ft.SnackBar(ft.Text("Acceso denegado a la interfaz de edición."))
            self.page.snack_bar.open = True
            self.load_catalog()
            return

        self.page.clean()
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER

        # US07 (Escenario 2): Todos los campos del formulario aparecen pre-cargados
        title_input = ft.TextField(label="Título", value=str(product.title), width=350)
        price_input = ft.TextField(label="Precio", value=str(product.price), width=350)
        desc_input = ft.TextField(label="Descripción", value=str(product.description), multiline=True, min_lines=3, width=350)
        image_input = ft.TextField(label="URL de imagen", value=str(product.image), width=350)
        category_dropdown = ft.Dropdown(
            label="Categoría",
            value=product.category if product.category in ["electronics", "jewelery", "men's clothing", "women's clothing"] else None,
            width=350,
            options=[
                ft.dropdown.Option("electronics"),
                ft.dropdown.Option("jewelery"),
                ft.dropdown.Option("men's clothing"),
                ft.dropdown.Option("women's clothing")
            ]
        )

        error_banner = ft.Text("", color="red", visible=False)
        loading_spinner = ft.ProgressRing(visible=False)
        save_button = ft.Button("Guardar Cambios", icon=ft.Icons.SAVE)

        def update_product(e):
            title_input.border_color = None
            price_input.border_color = None
            desc_input.border_color = None
            image_input.border_color = None
            category_dropdown.border_color = None
            error_banner.visible = False

            has_error = False

            # Validaciones de texto no vacío
            if not title_input.value or not title_input.value.strip():
                title_input.border_color = "red"
                has_error = True
            if not desc_input.value or not desc_input.value.strip():
                desc_input.border_color = "red"
                has_error = True
            if not image_input.value or not image_input.value.strip():
                image_input.border_color = "red"
                has_error = True
            if not category_dropdown.value:
                category_dropdown.border_color = "red"
                has_error = True

            # Validación de formato numérico para el precio
            parsed_price = None
            if not price_input.value or not price_input.value.strip():
                price_input.border_color = "red"
                has_error = True
            else:
                try:
                    parsed_price = float(price_input.value.strip())
                except ValueError:
                    price_input.border_color = "red"
                    has_error = True

            if has_error:
                error_banner.value = "Corrige los campos en rojo. El precio debe ser un número válido."
                error_banner.visible = True
                self.page.update()
                return

            # US07 (Reglas de negocio): Deshabilitar botón e indicar carga para evitar duplicados
            save_button.disabled = True
            loading_spinner.visible = True
            self.page.update()

            try:
                payload = {
                    "title": title_input.value.strip(),
                    "price": parsed_price,
                    "description": desc_input.value.strip(),
                    "image": image_input.value.strip(),
                    "category": category_dropdown.value
                }

                response = ApiService.actualizar_producto(product.id, payload)

                if response.status_code in [200, 201]:
                    # US07 (Escenario 1): Actualización exitosa (Simulación)
                    self.page.snack_bar = ft.SnackBar(ft.Text("Producto actualizado (Simulación)"))
                    self.page.snack_bar.open = True
                    # Refleja los cambios localmente en la vista de detalle
                    self.show_product_detail(product.id)
                else:
                    save_button.disabled = False
                    loading_spinner.visible = False
                    error_banner.value = f"Error en el servidor (Status {response.status_code})"
                    error_banner.visible = True
                    self.page.update()

            except Exception as ex:
                save_button.disabled = False
                loading_spinner.visible = False
                error_banner.value = f"Error al procesar actualización: {ex}"
                error_banner.visible = True
                self.page.update()

        save_button.on_click = update_product

        form_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(f"Editar Producto (ID: {product.id})", size=20, weight=ft.FontWeight.BOLD),
                        title_input,
                        price_input,
                        desc_input,
                        image_input,
                        category_dropdown,
                        error_banner,
                        loading_spinner,
                        ft.Row(
                            controls=[
                                save_button,
                                ft.Button("Cancelar", on_click=lambda _: self.show_product_detail(product.id))
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12
                ),
                padding=20
            )
        )

        self.page.add(form_card)
        self.page.update()

    # US08: Confirmación y lógica para eliminar producto
    def confirm_delete_product(self, product):
        # US08 (Escenario 3): Restricción de seguridad
        if self.session.user_role != "Administrador":
            self.page.snack_bar = ft.SnackBar(ft.Text("Acceso bloqueado: No tienes permisos para eliminar."))
            self.page.snack_bar.open = True
            return

        # US08 (Reglas de negocio): Confirmación obligatoria vía AlertDialog nativo
        def execute_delete(e):
            dialog.open = False
            self.page.update()

            try:
                response = ApiService.eliminar_producto(product.id)
                if response.status_code in [200, 201, 204]:
                    # US08 (Escenario 1): Notificación flotante de éxito y redirección al catálogo
                    self.page.snack_bar = ft.SnackBar(ft.Text(f"Producto '{product.title}' eliminado con éxito (Simulación)."))
                    self.page.snack_bar.open = True
                    self.load_catalog()
                else:
                    self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar en el servidor (Status {response.status_code})."))
                    self.page.snack_bar.open = True
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error de red al eliminar producto: {ex}"))
                self.page.snack_bar.open = True

        def cancel_delete(e):
            # US08 (Escenario 2): Cancela el borrado, cierra el cuadro de diálogo y mantiene la vista
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text("¿Estás seguro de eliminar este producto?"),
            actions=[
                ft.TextButton("Sí, eliminar", on_click=execute_delete),
                ft.TextButton("Cancelar", on_click=cancel_delete)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()