# Liquidación de Prestaciones Sociales Anuales (Nov.2024–Nov.2025)

## Resumen Ejecutivo  
Este informe compila la normativa vigente en Colombia para calcular la liquidación de prestaciones sociales (cesantías, intereses, prima, vacaciones) y finiquito de un trabajador privado con contrato (definido o indefinido) en el periodo 16 nov 2024–15 nov 2025. Se detallan los requisitos formales (contrato laboral, afiliación a seguridad social, no aplicable a contratistas de servicios) y la conformación de la Base de Liquidación (SBL), incluyendo salario básico, horas extras, comisiones, bonificaciones y auxilio de transporte o transporte:contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}. Se presentan las fórmulas legales actualizadas (2025) para cada prestación: Cesantías (SBL×días/360), Intereses (Cesantías×días×0.12/360), Prima (SBL×días semestrales/360) y Vacaciones (SBL×días/720):contentReference[oaicite:2]{index=2}:contentReference[oaicite:3]{index=3}. También se indican los parámetros oficiales 2025 (SMMLV=$1.423.500; auxilio transporte=$200.000 para salarios ≤2 SMMLV:contentReference[oaicite:4]{index=4}:contentReference[oaicite:5]{index=5}). El diseño de la herramienta CLI propuesta incluye validaciones (rechazar contrato de prestación de servicios, verificación de días laborados, tope de auxilio) y produce un JSON con el desglose de cada prestación, total liquidación, fecha límite de pago (día de terminación del contrato según Art.65 CST:contentReference[oaicite:6]{index=6}) y norma sustento. Se ejemplifica el cálculo con valores de 2025.

## Tabla de fuentes legales  

| Norma                                            | Artículos / Ítem           | URL                                                    | Vigencia               |
|--------------------------------------------------|----------------------------|--------------------------------------------------------|------------------------|
| **Cód. Sustantivo del Trabajo (CST)**            | Arts. 249-252 (Cesantías); 306-308 (Prima); 186-192 (Vacaciones); 161-167 (Jornada/Horas) | [Decreto 1072/2015 – Sector Trabajo (compila CST)](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=72173) | Vigente (varios años)  |
| **Ley 50 de 1990**                               | Art. 99 (intereses sobre cesantías)  | [Gestor Normativo – Ley 50/1990](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=281) | Vigente desde 1990     |
| **Decreto 1072 de 2015**                         | Arts. 2.2.1.3.1–3.5 (Cesantías e Intereses) | [Gestor Normativo – Decreto 1072/2015](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=72173) | Vigente desde 2015     |
| **Decreto 1572 de 2024**                         | Art. 1 (Salario mínimo 2025) | [Gestor Normativo – Decreto 1572/2024](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=257156) | 2025                  |
| **Decreto 1573 de 2024**                         | Art. 1 (Auxilio de transporte 2025) | [Gestor Normativo – Decreto 1573/2024](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=256836) | 2025                  |
| **CST Art. 65 (CST)**                            | Indemnización por mora (pago oportuno) | *Fuente oficial SUIN/Juriscol*                 | Vigente               |

## Requisitos formales  
La liquidación procede sólo al trabajador dependiente con **contrato de trabajo** (fijo o indefinido):contentReference[oaicite:7]{index=7}. Los contratos **de prestación de servicios** no generan prestaciones laborales:contentReference[oaicite:8]{index=8}. Aunque el contrato no sea escrito, se presume indefinido si se cumplen los elementos de subordinación y pago de salario:contentReference[oaicite:9]{index=9}:contentReference[oaicite:10]{index=10}. Además el trabajador debe estar afiliado y cotizando al sistema de seguridad social (salud, pensión, ARL). El finiquito se aplica en casos de terminación legal del vínculo (renuncia, despido, muerte, expiración del término, entre otros):contentReference[oaicite:11]{index=11}. 

## Base de Liquidación (SBL)  
La **Base de Liquidación (SBL)** incluye todas las remuneraciones habituales: salario básico, horas extras, recargos (nocturnos, dominicales), comisiones, bonificaciones y demás ingresos en dinero pactados como salario:contentReference[oaicite:12]{index=12}. Aunque el auxilio de transporte no es salario, debe adicionarse al SBL si el trabajador lo devenga:contentReference[oaicite:13]{index=13}. Para trabajadores internos (residen en el sitio de trabajo) no aplica transporte; en su lugar puede percibir **auxilio de transporte** de igual cuantía:contentReference[oaicite:14]{index=14}. Si el salario varía frecuentemente o incluye conceptos variables, la base legal para liquidar cesantías es el promedio del último año o del tiempo laborado si es menor a un año:contentReference[oaicite:15]{index=15}. 

## Fórmulas legales de cálculo  
- **Cesantías:** Según el Art. 249-250 CST, equivalen a un salario anual por cada año laborado (proporcional por días). Se calculan:  
  $$\text{Cesantías} = \frac{\text{SBL} \times \text{días trabajados}}{360}.$$  
- **Intereses sobre cesantías:** Ley 50/90 fija tasa 12% anual sobre la cesantía acumulada. Se calcula:  
  $$\text{Intereses} = \frac{\text{Cesantías} \times \text{días trabajados en año} \times 0.12}{360}$$  
  (o sea 1% mensual, según norma tradicional):contentReference[oaicite:16]{index=16}.  
- **Prima de servicios:** Art. 306-308 CST: 30 días de salario por año laboral. Se paga semestralmente (mitad el 30 de junio, mitad antes del 20 de diciembre). Fórmula:  
  $$\text{Prima} = \frac{\text{SBL} \times \text{días trabajados en el semestre}}{360} \times 360/180 = \frac{\text{SBL} \times \text{días semestrales}}{360},$$  
  lo que equivale a 15 días de salario por semestre trabajado:contentReference[oaicite:17]{index=17}.  
- **Vacaciones:** Art. 186-192 CST: 15 días hábiles por año trabajado. Equivalente proporcional:  
  $$\text{Vacaciones} = \frac{\text{SBL} \times \text{días a liquidar}}{720},$$  
  pues 360 días de trabajo generan 15 días de vacaciones (15/360 = 1/24, equivalente a multiplicar por días/720).  
- **Salario pendiente y horas extras:** Art. 161-167 CST establece la remuneración del trabajo ordinario (máx. 8h diarias, 48h semanales) y recargos por extras, nocturnos, festivos. Al liquidar se deben pagar los salarios devengados no cancelados, incluyendo recargos de jornada y horas extras pendientes.

En todos los cálculos, el SBL se usa en pesos (redondeos al peso). Las operaciones deben considerar comisiones variables prorrateadas y decimales con redondeo estándar (2 decimales o unidades monetarias). 

## Parámetros oficiales 2025  
- **Salario Mínimo 2025:** Decretado en $1.423.500 mensuales:contentReference[oaicite:18]{index=18} (SMMLV).  
- **Auxilio de Transporte 2025:** $200.000 mensuales:contentReference[oaicite:19]{index=19}. Se otorga sólo a trabajadores que devenguen hasta 2 SMMLV ($2.847.000) según Art. 1 Decreto 1573/2024:contentReference[oaicite:20]{index=20}.  
- **Topes de cotización:** Los ingresos superiores a 25 SMMLV no aumentan base para parafiscales o pensión (tope definido en la Ley 100/1993, actualizado anualmente).  
- **Días laborales:** Se calcula con base en calendario (se excluyen días de incapacidad, licencias no laboradas, etc.).  

Estos parámetros (SMMLV, auxilio) deben actualizarse anualmente en el script.  

## Diseño de la herramienta CLI  
- **Entradas:** fecha de ingreso, fecha de corte anual (p. ej. 15 de noviembre), salario o SBL mensual (o lista de salarios mensuales si varía), tipo de contrato (término fijo o indefinido), motivo de terminación, indicador de auxilio (transporte o conectividad).  
- **Cálculo:** Determinar días totales trabajados; calcular SBL mensual o promedio anual según variaciones:contentReference[oaicite:21]{index=21}; aplicar las fórmulas antes descritas para cada prestación. Incluir beneficios legales (aplica auxilio si cumple topes).  
- **Salidas (JSON):** valores individuales de cada prestación (cesantías, intereses, prima, vacaciones, salarios pendientes, horas extras), total de la liquidación, fecha límite de pago (misma fecha de terminación del contrato, según Art. 65 CST):contentReference[oaicite:22]{index=22}, e identificación de las normas aplicadas.  
- **Validaciones:** Rechazar si el vínculo es contrato de prestación de servicios. Alertar si los días cotizados son inferiores al año completo (calcular prestaciones proporcionales). Verificar que el salario base no exceda 2 SMMLV si se intenta incluir auxilio de transporte:contentReference[oaicite:23]{index=23}.  
- **Fecha límite de pago:** Art. 65 CST no da plazo posterior; la liquidación debe pagarse en la misma fecha de terminación. En mora se genera indemnización moratoria (un día de salario por día de retraso, tope 24 meses):contentReference[oaicite:24]{index=24}:contentReference[oaicite:25]{index=25}. 

## Ejemplo de ejecución (2025)  
Suponga un trabajador que ingresó el 16 Nov 2024 y termina el 15 Nov 2025, con salario base $2.000.000 mensual, y vive en la empresa (se aplica auxilio de transporte de $200.000 en vez de transporte):contentReference[oaicite:26]{index=26}:contentReference[oaicite:27]{index=27}. El SBL efectivo mensual será $2.200.000. Con 360 días trabajados:  
- Cesantías = 2.200.000×360/360 = $2.200.000.  
- Intereses = 2.200.000×360×0.12/360 = $264.000.  
- Prima semestral = 2.200.000×180/360 = $1.100.000 (por semestre, total $2.200.000 anual).  
- Vacaciones = 2.200.000×360/720 = $1.100.000.  
- *Total liquidación* ≈ $5.764.000 (sin incluir horas extras ni indemnizaciones). La fecha límite de pago es el 15 Nov 2025 (Art.65 CST):contentReference[oaicite:28]{index=28}. 

El script CLI devolvería un JSON con cada componente valorizado, los artículos aplicables (p.ej., `"cesantias": {"valor": 2200000, "norma": "Art.249-250 CST"}`, etc.), y la suma total. 

## Función `liquidar()` (pseudocódigo)  

```python
def liquidar(fecha_ingreso, fecha_liquidacion, SBL_mensual, contrato, motivo, auxilio_aplica):
    if contrato == 'prestación_servicios':
        raise ValueError("Contrato de prestación de servicios no genera liquidación.")
    dias = (fecha_liquidacion - fecha_ingreso).days + 1
    # Calcular SBL: si salarios variables, usar promedio de últimos 12 meses
    # Sumar horas extras promedio, recargos, comisiones, bonificaciones
    # Incluir auxilio (transporte o conectividad) si aplica según tope salarial
    SBL = SBL_mensual
    if auxilio_aplica:
        SBL += 200000  # auxilio transporte o conectividad 2025
    
    # Cálculos de prestaciones
    cesantias = SBL * dias / 360
    intereses = cesantias * dias * 0.12 / 360
    prima = SBL * (min(dias, 180)) / 360  # calculo semestral (dos semestres por año)
    vacaciones = SBL * dias / 720
    # Salario pendiente y horas extras: sumar valores devengados pero no pagados
    salario_pendiente = calcular_salario_pendiente(...)
    horas_extras = calcular_horas_extras(...)
    
    total = cesantias + intereses + prima + vacaciones + salario_pendiente + horas_extras
    # Fecha límite de pago: misma fecha de terminación del contrato
    fecha_limite = fecha_liquidacion
    
    return {
        "cesantias": {"valor": round(cesantias, 0), "norma": "Art.249-252 CST"},
        "intereses_cesantias": {"valor": round(intereses, 0), "norma": "Ley 50/1990, Art.99 CST"},
        "prima": {"valor": round(prima, 0), "norma": "Art.306-308 CST"},
        "vacaciones": {"valor": round(vacaciones, 0), "norma": "Art.186-192 CST"},
        "salario_pendiente": {"valor": salario_pendiente, "norma": "Art.161-167 CST"},
        "horas_extras": {"valor": horas_extras, "norma": "Art.161-167 CST"},
        "total": round(total, 0),
        "fecha_limite_pago": fecha_limite.isoformat(),
        "normas_aplicadas": ["Art. 249 CST", "Ley 50/90, Art.99", "Art.306 CST", "Art.65 CST"]
    }
