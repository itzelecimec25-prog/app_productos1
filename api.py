# Importa el conector de MySQL
import mysql.connector  # type: ignore
import jwt  # type: ignore
from modelos.productos import Product

# Clase simuladora de respuesta HTTP para mantener compatibilidad con app.py sin cambiar nada
class MockResponse:
    def __init__(self, status_code: int, data: dict):
        self.status_code = status_code
        self._data = data

    def json(self):
        return self._data

# Define la clase ApiService conectada a MySQL Workbench
class ApiService:
    DB_CONFIG = {
        "host": "localhost",
        "user": "root",          # Cambia por tu usuario de MySQL si es diferente
        "password": "Jaz_007itzel",# Cambia por tu contraseña de MySQL
        "database": "api" # Nombre de tu base de datos en Workbench
    }

    @classmethod
    def _get_connection(cls):
        return mysql.connector.connect(**cls.DB_CONFIG)

    @classmethod
    def login(cls, username, password):
        try:
            conn = cls._get_connection()
            cursor = conn.cursor(dictionary=True)
            # Busca al usuario validando el username y el password exactos en la base de datos
            cursor.execute("SELECT id, username, role FROM usuarios WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                # Codifica un token simulado conteniendo el ID del usuario en el campo 'sub' (para SessionService)
                fake_token = jwt.encode({"sub": user["id"]}, "secret", algorithm="HS256")
                return MockResponse(200, {"token": fake_token})
            else:
                return MockResponse(401, {"message": "Credenciales inválidas"})
        except Exception as ex:
            raise Exception(f"Error en base de datos al iniciar sesión: {ex}")

    @classmethod
    def obtener_categorias(cls):
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM productos")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return [row[0] for row in rows]
        except Exception as ex:
            raise Exception(f"Error al obtener categorías de MySQL: {ex}")

    @classmethod
    def obtener_productos(cls, category=None):
        try:
            conn = cls._get_connection()
            cursor = conn.cursor(dictionary=True)
            if category:
                cursor.execute("SELECT id, title, price, description, category, image FROM productos WHERE category = %s", (category,))
            else:
                cursor.execute("SELECT id, title, price, description, category, image FROM productos")
            items = cursor.fetchall()
            cursor.close()
            conn.close()
            return [Product.from_json(item) for item in items]
        except Exception as ex:
            raise Exception(f"Error al consultar productos en MySQL: {ex}")

    @classmethod
    def obtener_detalle_producto(cls, product_id: int):
        try:
            conn = cls._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, title, price, description, category, image FROM productos WHERE id = %s", (product_id,))
            item = cursor.fetchone()
            cursor.close()
            conn.close()
            if item:
                return Product.from_json(item)
            raise Exception("Producto no disponible")
        except Exception as ex:
            raise Exception(f"Error al obtener detalle en MySQL: {ex}")

    @classmethod
    def crear_producto(cls, payload: dict):
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            query = "INSERT INTO productos (title, price, description, category, image) VALUES (%s, %s, %s, %s, %s)"
            values = (payload["title"], payload["price"], payload["description"], payload["category"], payload["image"])
            cursor.execute(query, values)
            conn.commit()
            new_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return MockResponse(201, {"id": new_id, **payload})
        except Exception as ex:
            raise Exception(f"Error al crear producto en MySQL: {ex}")

    @classmethod
    def actualizar_producto(cls, product_id: int, payload: dict):
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            query = "UPDATE productos SET title = %s, price = %s, description = %s, category = %s, image = %s WHERE id = %s"
            values = (payload["title"], payload["price"], payload["description"], payload["category"], payload["image"], product_id)
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            return MockResponse(200, {"id": product_id, **payload})
        except Exception as ex:
            raise Exception(f"Error al actualizar producto en MySQL: {ex}")

    @classmethod
    def eliminar_producto(cls, product_id: int):
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM productos WHERE id = %s", (product_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return MockResponse(200, {"id": product_id})
        except Exception as ex:
            raise Exception(f"Error al eliminar producto en MySQL: {ex}")