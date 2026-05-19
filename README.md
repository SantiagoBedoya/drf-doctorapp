# Doctor App — Django REST Framework Conceptos

Proyecto de gestión de citas médicas que implementa los siguientes conceptos de **Django REST Framework (DRF)**:

---

## 1. Serializers

### ModelSerializer
Transforma modelos Django a/desde JSON automáticamente. Solo declaras el modelo y los campos.

```python
class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'
```

**Archivos:** `doctors/serializers.py`, `bookings/serializers.py`, `patients/serializers.py`

### Nested Serializer
Un serializer dentro de otro para representar relaciones. Aquí `PatientSerializer` incluye todas las citas del paciente:

```python
appointments = AppointmentSerializer(many=True, read_only=True, source='patient')
```

**Archivo:** `patients/serializers.py:7`

### SerializerMethodField
Campo de solo lectura cuyo valor se calcula con un método. Ejemplo: calcular edad desde la fecha de nacimiento:

```python
age = serializers.SerializerMethodField()

def get_age(self, obj):
    return date.today().year - obj.date_of_birth.year
```

**Archivo:** `patients/serializers.py:8,25-27`

---

## 2. Validación

### Field-level validation (`validate_<campo>`)
Valida un campo específico. DRF llama automáticamente `validate_email()` al procesar el serializer:

```python
def validate_email(self, value):
    if '@example.com' not in value:
        raise serializers.ValidationError("El email debe ser de example.com")
    return value
```

**Archivo:** `doctors/serializers.py:9-12`

### Object-level validation (`validate`)
Valida múltiples campos entre sí. Se ejecuta después de las validaciones individuales:

```python
def validate(self, attrs):
    if len(attrs.get('contact_number', '')) < 10 and attrs.get('is_on_vacation'):
        raise serializers.ValidationError("...")
    return attrs
```

**Archivo:** `doctors/serializers.py:14-17`

### raise_exception=True
`serializer.is_valid(raise_exception=True)` lanza automáticamente un error HTTP 400 si los datos no son válidos.

**Archivo:** `doctors/viewsets.py:44`

---

## 3. ViewSets

### ModelViewSet
Clase que implementa **las 6 operaciones CRUD** automáticamente: list, create, retrieve, update, partial_update, destroy.

```python
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
```

**Archivos:** `doctors/viewsets.py:17-66`, `bookings/viewsets.py:7-14`, `patients/viewsets.py:11-23`

---

## 4. Custom Actions (@action)

### @action(detail=True)
Agrega endpoints personalizados a un ViewSet más allá del CRUD estándar.

- **`set_on_vacation`** / **`set_off_vacation`**: Cambian el estado del doctor (POST).
- **`appointments`**: Lista (GET) o crea (POST) citas de un doctor.

```python
@action(['POST'], detail=True, url_path='set-on-vacation')
def set_on_vacation(self, request, pk=None):
    doctor = self.get_object()
    doctor.is_on_vacation = True
    doctor.save()
    return Response({"status": "doctor en vacaciones"})
```

**Archivo:** `doctors/viewsets.py:22-51`

### self.get_object()
Obtiene la instancia del modelo usando el `pk` de la URL. Disponible en cualquier action detail.

### many=True
Indica que el serializer procesará **una lista** de objetos en lugar de uno solo:

```python
AppointmentSerializer(appointments, many=True)
```

**Archivo:** `doctors/viewsets.py:50`

---

## 5. Generic Views (Class-Based Views)

Alternativa a ViewSets. Views genéricas para operaciones específicas:

| Vista | Qué hace |
|-------|----------|
| `ListCreateAPIView` | Lista y crea recursos (GET + POST) |
| `RetrieveUpdateDestroyAPIView` | Obtiene, actualiza y elimina un recurso (GET + PUT + PATCH + DELETE) |
| `ListAPIView` + `CreateAPIView` (herencia múltiple) | Combinación manual de list y create |

```python
class ListDoctorsView(ListCreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    allowed_methods = ['GET', 'POST']
```

**Archivos:** `doctors/views.py:6-57`, `bookings/views.py:6-28`, `patients/views.py:6-15`

### get_queryset() personalizado
Filtra los datos según parámetros de la URL. Ejemplo: obtener disponibilidades de un doctor específico:

```python
def get_queryset(self):
    return DoctorAvailability.objects.filter(doctor_id=self.kwargs['pk'])
```

**Archivos:** `doctors/views.py:33-34`, `bookings/views.py:19-20`

### lookup_url_kwarg
Especifica el nombre del parámetro URL para el lookup. Útil cuando hay múltiples lookups anidados:

```python
lookup_url_kwarg = 'avail_pk'
```

**Archivos:** `doctors/views.py:39,54`, `bookings/views.py:25`

### allowed_methods
Restringe los métodos HTTP permitidos en una vista:

```python
allowed_methods = ['GET', 'POST']  # Solo lectura y creación, sin PUT/DELETE
```

**Archivos:** `doctors/views.py:7,13`, `patients/views.py:7`

---

## 6. Routers

### DefaultRouter
Genera automáticamente las rutas RESTful para los ViewSets.

```
router.register('doctors', DoctorViewSet)
# Genera: GET /doctors/, POST /doctors/, GET /doctors/{pk}/, PUT /doctors/{pk}/, DELETE /doctors/{pk}/
```

**Archivos:** `doctors/urls.py:10-16`, `bookings/urls.py:5-9`, `patients/urls.py:9-14`

---

## 7. Permisos

### BasePermission (permiso personalizado)
Clase base para crear permisos propios. `IsDoctor` solo permite acceso a usuarios del grupo "doctors":

```python
class IsDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='doctors').exists()
```

**Archivo:** `doctors/permissions.py:3-5`

### IsAuthenticatedOrReadOnly (built-in)
Permite lectura sin autenticación, pero requiere autenticación para escribir.

### permission_classes
Lista de permisos aplicados a un ViewSet. Se evalúan en orden:

```python
permission_classes = [IsAuthenticatedOrReadOnly, IsDoctor]
```

**Archivo:** `doctors/viewsets.py:20`

---

## 8. Autenticación

### SessionAuthentication
Autenticación basada en sesiones del navegador. Ideal para la API navegable de DRF.

```python
'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication']
```

### rest_framework.urls (login/logout)
Incluye las vistas de login/logout de DRF para la API navegable:

```python
path('api-auth', include('rest_framework.urls'))
```

**Archivo:** `doctorapp/urls.py:22`

---

## 9. Throttling (Límite de peticiones)

Controla cuántas peticiones puede hacer un cliente en un tiempo determinado.

| Throttle | Afecta a | Límite |
|----------|----------|--------|
| `AnonRateThrottle` | Usuarios no autenticados | 5/minuto |
| `UserRateThrottle` | Usuarios autenticados | 1000/minuto |

**Archivo:** `doctorapp/settings.py:128-135`

---

## 10. Response y Status Codes

### Response
Clase de DRF para devolver respuestas HTTP. Acepta datos serializados y códigos de estado.

```python
return Response({"status": "ok"}, status=status.HTTP_201_CREATED)
```

### status
Constantes con nombres legibles para códigos HTTP: `HTTP_200_OK`, `HTTP_201_CREATED`, `HTTP_204_NO_CONTENT`, `HTTP_400_BAD_REQUEST`, `HTTP_403_FORBIDDEN`, `HTTP_404_NOT_FOUND`.

**Archivos:** `doctors/viewsets.py:2,27`, `doctors/tests.py:4`

---

## 11. API Schema / Documentación (drf-spectacular)

Genera documentación OpenAPI automática a partir del código.

| Endpoint | Qué muestra |
|----------|-------------|
| `/api/schema/` | Schema OpenAPI en formato YAML |
| `/api/schema/swagger-ui/` | Interfaz Swagger UI interactiva |
| `/api/schema/redoc/` | Documentación ReDoc |

**Archivo:** `docs/urls.py:2-9`

---

## 12. Testing

### APITestCase
Clase base para tests de API. Incluye `self.client` para hacer peticiones HTTP de prueba.

### self.client (get, post, put, patch, delete)
Cliente de prueba similar a `requests`. Soporta `format="json"`:

```python
response = self.client.get('/api/doctors/')
response = self.client.post('/api/doctors/', data, format='json')
```

### force_authenticate()
Autentica al cliente de prueba sin necesidad de credenciales reales:

```python
self.client.force_authenticate(user=self.doctor_user)
```

**Archivo:** `doctors/tests.py:5-558`
