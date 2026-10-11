# Importa la librería PyJWT para decodificar y trabajar con tokens JWT
import jwt  # type: ignore

# Define la clase para gestionar la sesión del usuario
class SessionService:
    # Inicializa los atributos de estado de la sesión
    def __init__(self):
        self.auth_token = None
        self.user_id = None
        self.user_role = None

    # Método que verifica si existe una sesión activa
    def esta_autenticado(self) -> bool:
        # Devuelve True si hay un token guardado, o False en caso contrario
        return self.auth_token is not None

    # Método para iniciar sesión a partir de un token recibido
    def iniciar_sesion(self, token: str):
        # Guarda el token recibido en el atributo de la instancia
        self.auth_token = token
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        # Extrae el identificador del usuario del campo sub
        raw_user_id = decoded_token.get("sub")
        try:
            # Convierte el ID a entero si es un valor numérico
            self.user_id = int(raw_user_id)
        # Si ocurre un error de valor o tipo al convertir
        except (ValueError, TypeError):
            # Conserva el ID en su formato original
            self.user_id = raw_user_id
        
        # Asigna el rol correspondiente llamando al método interno con el ID del usuario
        self.user_role = self._calcular_rol(self.user_id)

    # Método para limpiar los datos y cerrar la sesión actual
    def cerrar_sesion(self):
        self.auth_token = None
        self.user_id = None
        self.user_role = None

    # Método privado que determina el rol según el ID del usuario
    def _calcular_rol(self, user_id) -> str:
        # Evalúa si el ID pertenece a la lista de administradores
        if user_id in [1, 2]:
            return "Administrador"
        # Evalúa si el ID corresponde al auditor
        elif user_id == 3:
            return "Auditor"
        # Si no coincide con los ID anteriores es cliente
        else:
            return "Cliente"