# Modulo de Parametros - liquidator.params

Modulo para carga, validacion y versionamiento de parametros legales del sistema de liquidacion de nomina Colombia 2025.

## Uso Rapido

### Carga Simple de Parametros

```python
from pathlib import Path
from liquidator.params import ParamsLoader

# Inicializar loader
loader = ParamsLoader(base_dir=Path("params"))

# Cargar parametros del ano 2025
params = loader.load(year=2025, validate=False)

# Acceder a valores
smmlv = params["SMMLV"]  # 1423500
auxilio = params["AUXILIO_TRANS"]  # 200000
```

### Carga con Validacion de Schema

```python
from pathlib import Path
from liquidator.params import ParamsLoader, ParamsValidator

# Crear validator
validator = ParamsValidator()

# Inicializar loader con validator
loader = ParamsLoader(base_dir=Path("params"), validator=validator)

# Cargar y validar automaticamente
params = loader.load(year=2025, validate=True)
```

### Versionamiento y Trazabilidad

```python
from pathlib import Path
from liquidator.params import ParamsLoader, ParamsVersioning

loader = ParamsLoader(base_dir=Path("params"))
versioning = ParamsVersioning()

# Cargar parametros
params_path = Path("params/2025.json")
params = loader.load(year=2025, path=params_path, validate=False)

# Registrar version
version_info = versioning.register_version(
    year=2025,
    path=params_path,
    data=params
)

print(f"Version: {version_info.version}")
print(f"Hash: {version_info.hash_sha256}")
print(f"Fecha: {version_info.fecha_carga}")

# Verificar integridad mas tarde
is_valid = versioning.verify_integrity(year=2025, current_path=params_path)
if not is_valid:
    print("ADVERTENCIA: El archivo de parametros fue modificado!")
```

### Validacion Manual de Schema

```python
from pathlib import Path
from liquidator.params import ParamsValidator

# Cargar schema
validator = ParamsValidator()
validator.load_schema(Path("params/schema.json"))

# Validar datos
data = {
    "year": 2025,
    "salario_minimo": 1423500
}

try:
    validator.validate(data)
    print("Validacion exitosa")
except ValidationError as e:
    print(f"Error de validacion: {e}")
```

## API Reference

### ParamsLoader

#### Constructor
```python
ParamsLoader(base_dir: Path | str, validator: Optional[ParamsValidator] = None)
```

#### Metodos

**`load(year, validate=True, path=None, schema_path=None) -> Dict[str, Any]`**
- Carga parametros del ano especificado
- `validate`: Si True y hay validator, valida contra schema
- `path`: Path explicito al archivo (opcional)
- `schema_path`: Path explicito al schema (opcional)
- Retorna: Diccionario con parametros

**`load_raw(source: ParamsSource) -> Dict[str, Any]`**
- Carga sin validacion
- Lanza `ParamsError` si hay problemas

**`resolve_paths(year, explicit_path=None, schema_path=None) -> ParamsSource`**
- Resuelve paths de archivo y schema
- Usa convencion `{year}.json` y `schema.json` por defecto

### ParamsValidator

#### Constructor
```python
ParamsValidator(schema: Optional[Dict[str, Any]] = None)
```

#### Metodos

**`validate(data: Dict[str, Any]) -> bool`**
- Valida datos contra schema
- Lanza `ValidationError` si falla
- Retorna True si es exitoso

**`load_schema(schema_path: Path) -> None`**
- Carga schema desde archivo JSON
- Lanza `ValidationError` si hay problemas

**`ensure_schema_loaded(schema_path: Optional[Path]) -> None`**
- Carga schema solo si no esta cargado ya
- Util para carga lazy

#### Atributos

**`last_validation_message: Optional[str]`**
- Mensaje de la ultima operacion de validacion

### ParamsVersioning

#### Constructor
```python
ParamsVersioning()
```

#### Metodos

**`calculate_file_hash(path: Path) -> str`**
- Calcula SHA256 del archivo
- Retorna: Hash hexadecimal de 64 caracteres

**`calculate_data_hash(data: Dict[str, Any]) -> str`**
- Calcula SHA256 deterministico de datos
- Ordena claves para consistencia
- Retorna: Hash hexadecimal de 64 caracteres

**`register_version(year, path, data=None) -> VersionInfo`**
- Registra version de parametros
- `data`: Diccionario con parametros (opcional)
- Retorna: VersionInfo con metadata

**`get_version(year: int) -> Optional[VersionInfo]`**
- Obtiene informacion de version registrada
- Retorna None si no existe

**`verify_integrity(year, current_path) -> bool`**
- Verifica que archivo no fue modificado
- Compara hash actual con hash registrado
- Retorna True si coinciden

**`to_dict() -> Dict[int, Dict[str, Any]]`**
- Exporta todas las versiones a diccionario
- Util para auditoria y logging

### VersionInfo (dataclass)

```python
@dataclass(frozen=True)
class VersionInfo:
    year: int
    version: str
    hash_sha256: str
    fecha_carga: str
    metadata: Optional[Dict[str, Any]] = None
```

## Excepciones

### ParamsError
Lanzada por ParamsLoader cuando:
- Archivo de parametros no encontrado
- JSON invalido en archivo

### ValidationError
Lanzada por ParamsValidator cuando:
- Schema no encontrado
- Schema JSON invalido
- Datos no cumplen schema
- Schema path requerido pero no provisto

## Ejemplo Completo

```python
from pathlib import Path
from liquidator.params import ParamsLoader, ParamsValidator, ParamsVersioning

# Setup
base_dir = Path("params")
validator = ParamsValidator()
loader = ParamsLoader(base_dir=base_dir, validator=validator)
versioning = ParamsVersioning()

# Cargar parametros con validacion
try:
    params = loader.load(year=2025, validate=True)
    print(f"Parametros cargados: SMMLV = ${params['SMMLV']:,}")
    
    # Registrar version para auditoria
    params_path = base_dir / "2025.json"
    version_info = versioning.register_version(
        year=2025,
        path=params_path,
        data=params
    )
    
    print(f"Version registrada: {version_info.version}")
    print(f"Hash: {version_info.hash_sha256[:16]}...")
    
    # Exportar info de versiones
    versions = versioning.to_dict()
    print(f"Total versiones registradas: {len(versions)}")
    
except ParamsError as e:
    print(f"Error cargando parametros: {e}")
except ValidationError as e:
    print(f"Error de validacion: {e}")
```

## Notas

- Todos los archivos deben estar en UTF-8
- jsonschema es opcional pero recomendado para produccion
- Los hashes son deterministicos (mismo contenido = mismo hash)
- Los timestamps usan ISO 8601 con timezone
- El modulo es compatible con ASCII segun configuracion del proyecto
